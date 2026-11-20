from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginate(objects_list, request, per_page=10, max_page_links=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # Вычисляем диапазон страниц для отображения
    current_page = page.number
    total_pages = paginator.num_pages

    half = max_page_links // 2
    if current_page <= half + 1:
        start_page = 1
        end_page = min(max_page_links, total_pages)
    elif current_page >= total_pages - half:
        start_page = max(1, total_pages - max_page_links + 1)
        end_page = total_pages
    else:
        start_page = current_page - half
        end_page = current_page + half

    page.page_range_compact = range(start_page, end_page + 1)
    page.show_first_link = start_page > 1
    page.show_last_link = end_page < total_pages

    return page