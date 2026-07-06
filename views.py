import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Category, MenuItem, Table, Order, OrderItem


def menu_view(request):
    table_number = request.GET.get('table', '1')
    try:
        table = Table.objects.get(number=int(table_number))
        if table.status == Table.AVAILABLE:
            table.status = Table.OCCUPIED
            table.save()
    except (Table.DoesNotExist, ValueError):
        table = None
    categories = Category.objects.filter(is_active=True).prefetch_related(
        'items'
    )
    return render(request, 'restaurant/menu.html', {
        'table_number': table_number,
        'table': table,
        'categories': categories,
    })


def kitchen_view(request):
    return render(request, 'restaurant/kitchen.html')


def admin_dashboard(request):
    from django.db.models import Sum, Count
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today)
    stats = {
        'total_revenue': today_orders.filter(payment_status='paid').aggregate(s=Sum('total_amount'))['s'] or 0,
        'total_orders': today_orders.count(),
        'pending_orders': Order.objects.filter(status__in=['pending','preparing']).count(),
        'tables_occupied': Table.objects.filter(status='occupied').count(),
        'tables_total': Table.objects.count(),
    }
    tables = Table.objects.all()
    recent_orders = Order.objects.select_related('table').prefetch_related('items')[:20]
    return render(request, 'restaurant/admin_dashboard.html', {
        'stats': stats, 'tables': tables, 'recent_orders': recent_orders,
    })


# ── REST APIs ──────────────────────────────────────────────────────────────────

def api_menu(request):
    cats = []
    for cat in Category.objects.filter(is_active=True).prefetch_related('items'):
        items = []
        for item in cat.items.filter(is_available=True):
            items.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'emoji': item.emoji,
                'image': request.build_absolute_uri(item.image.url) if item.image else None,
                'food_type': item.food_type,
                'is_bestseller': item.is_bestseller,
                'is_new': item.is_new,
                'spice_level': item.spice_level,
            })
        if items:
            cats.append({'id': cat.id, 'name': cat.name, 'slug': cat.slug, 'icon': cat.icon, 'items': items})
    return JsonResponse({'categories': cats})


@csrf_exempt
@require_http_methods(['POST'])
def api_place_order(request):
    try:
        data = json.loads(request.body)
        table_number = data.get('table_number')
        items_data = data.get('items', [])
        special_instructions = data.get('special_instructions', '')

        if not table_number or not items_data:
            return JsonResponse({'error': 'table_number and items required'}, status=400)

        table = get_object_or_404(Table, number=table_number)
        order = Order.objects.create(
            table=table,
            special_instructions=special_instructions,
            status=Order.PENDING,
        )
        for item_data in items_data:
            menu_item = MenuItem.objects.get(id=item_data['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                item_name=menu_item.name,
                item_price=menu_item.price,
                quantity=item_data['quantity'],
                special_note=item_data.get('note', ''),
            )
        order.calculate_totals()
        table.status = Table.OCCUPIED
        table.save()
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'total': float(order.total_amount),
            'status': order.status,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_orders(request):
    status_filter = request.GET.get('status')
    qs = Order.objects.select_related('table').prefetch_related('items__menu_item')
    if status_filter:
        qs = qs.filter(status=status_filter)
    else:
        qs = qs.exclude(status__in=['served','paid'])
    orders = []
    for o in qs[:50]:
        orders.append({
            'id': o.id,
            'order_id': o.order_id,
            'table': o.table.number if o.table else None,
            'status': o.status,
            'payment_status': o.payment_status,
            'total': float(o.total_amount),
            'special_instructions': o.special_instructions,
            'created_at': o.created_at.isoformat(),
            'items': [{'name': i.item_name, 'qty': i.quantity, 'price': float(i.item_price)} for i in o.items.all()],
        })
    return JsonResponse({'orders': orders})


@csrf_exempt
@require_http_methods(['POST'])
def api_update_order_status(request, order_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        if new_status == 'paid':
            order.payment_status = 'paid'
            order.save()
            if order.table:
                order.table.status = Table.AVAILABLE
                order.table.save()
        return JsonResponse({'success': True, 'status': order.status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_tables(request):
    tables = [{'number': t.number, 'status': t.status, 'capacity': t.capacity} for t in Table.objects.all()]
    return JsonResponse({'tables': tables})


def qr_codes_view(request):
    tables = Table.objects.all()
    return render(request, 'restaurant/qr_codes.html', {'tables': tables, 'request': request})


@csrf_exempt
@require_http_methods(['POST'])
def generate_qr(request, table_number):
    from django.shortcuts import redirect
    table = get_object_or_404(Table, number=table_number)
    table.generate_qr()
    table.save()
    return redirect('/qr-codes/')
@csrf_exempt
@require_http_methods(['POST'])
def cash_payment(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order.payment_status = 'paid'
        order.payment_method = 'cash'
        order.status = 'served'
        order.save()
        if order.table:
            order.table.status = 'available'
            order.table.save()
        return JsonResponse({'success': True, 'order_id': order.order_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)