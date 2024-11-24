from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Keywords, TopKeywords

# 키워드 추가 또는 업데이트 시 호출
@receiver(post_save, sender=Keywords)
def update_top_keywords_on_save(sender, instance, **kwargs):
    keyword = instance.keyword
    top_keyword, created = TopKeywords.objects.get_or_create(keyword=keyword)
    if created:
        # 새 키워드인 경우, count 초기화
        top_keyword.count = 1
    else:
        # 기존 키워드인 경우, count 증가
        top_keyword.count = Keywords.objects.filter(keyword=keyword).count()
    top_keyword.save()

# 키워드 삭제 시 호출
@receiver(post_delete, sender=Keywords)
def update_top_keywords_on_delete(sender, instance, **kwargs):
    keyword = instance.keyword
    try:
        top_keyword = TopKeywords.objects.get(keyword=keyword)
        new_count = Keywords.objects.filter(keyword=keyword).count()
        if new_count == 0:
            # 더 이상 존재하지 않으면 삭제
            top_keyword.delete()
        else:
            # 존재하면 count 업데이트
            top_keyword.count = new_count
            top_keyword.save()
    except TopKeywords.DoesNotExist:
        pass