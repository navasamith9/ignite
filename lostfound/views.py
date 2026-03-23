from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from .models import LostItem, FoundItem, MatchNotification
from .forms import LostItemForm, FoundItemForm
from difflib import SequenceMatcher
from datetime import date

def calculate_match_score(lost_item, found_item):
    """Calculate similarity score between lost and found items"""
    score = 0
    
    # Title similarity (40% weight)
    title_similarity = SequenceMatcher(None, lost_item.title.lower(), found_item.title.lower()).ratio()
    score += title_similarity * 40
    
    # Category match (20% weight)
    if lost_item.category == found_item.category:
        score += 20
    
    # Location similarity (20% weight)
    location_similarity = SequenceMatcher(None, lost_item.location.lower(), found_item.location.lower()).ratio()
    score += location_similarity * 20
    
    # Description keywords match (20% weight)
    lost_words = set(lost_item.description.lower().split())
    found_words = set(found_item.description.lower().split())
    if lost_words and found_words:
        common_words = lost_words.intersection(found_words)
        word_similarity = len(common_words) / max(len(lost_words), 1)
        score += word_similarity * 20
    
    return int(min(100, score))

@login_required
def lost_items_view(request):
    items = LostItem.objects.all().order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    context = {
        'items': items,
        'categories': LostItem.CATEGORY_CHOICES,
        'type': 'lost',
        'today': date.today(),
    }
    return render(request, 'lostfound/lost_items.html', context)

@login_required
def found_items_view(request):
    items = FoundItem.objects.all().order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    context = {
        'items': items,
        'categories': FoundItem.CATEGORY_CHOICES,
        'type': 'found',
        'today': date.today(),
    }
    return render(request, 'lostfound/found_items.html', context)

@login_required
def report_lost_view(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            
            # Check for potential matches with found items
            found_items = FoundItem.objects.filter(status='pending')
            matches_found = 0
            
            for found_item in found_items:
                score = calculate_match_score(item, found_item)
                if score >= 60:  # High confidence match
                    MatchNotification.objects.create(
                        lost_item=item,
                        found_item=found_item,
                        match_score=score
                    )
                    matches_found += 1
                    
                    # Send notification email
                    try:
                        send_mail(
                            "Potential Match Found for Lost Item",
                            f"We found a potential match for your lost item '{item.title}'. "
                            f"Match confidence: {score}%. Check your dashboard for details.",
                            settings.DEFAULT_FROM_EMAIL,
                            [item.contact_email],
                            fail_silently=True,
                        )
                    except:
                        pass
            
            if matches_found > 0:
                messages.success(request, f'Lost item reported successfully! Found {matches_found} potential matches.')
            else:
                messages.success(request, 'Lost item reported successfully! We will notify you if there\'s a match.')
            
            return redirect('lostfound:lost_items')
    else:
        form = LostItemForm()
    
    context = {
        'form': form,
        'today': date.today(),
    }
    return render(request, 'lostfound/report_lost.html', context)

@login_required
def report_found_view(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            
            # Check for potential matches with lost items
            lost_items = LostItem.objects.filter(status='pending')
            matches_found = 0
            
            for lost_item in lost_items:
                score = calculate_match_score(lost_item, item)
                if score >= 60:
                    MatchNotification.objects.create(
                        lost_item=lost_item,
                        found_item=item,
                        match_score=score
                    )
                    matches_found += 1
                    
                    # Send notification email
                    try:
                        send_mail(
                            "Potential Match Found for Lost Item",
                            f"Someone found an item matching your lost '{lost_item.title}'. "
                            f"Match confidence: {score}%. Check your dashboard for details.",
                            settings.DEFAULT_FROM_EMAIL,
                            [lost_item.contact_email],
                            fail_silently=True,
                        )
                    except:
                        pass
            
            if matches_found > 0:
                messages.success(request, f'Found item reported successfully! Found {matches_found} potential matches.')
            else:
                messages.success(request, 'Found item reported successfully! We will notify potential owners.')
            
            return redirect('lostfound:found_items')
    else:
        form = FoundItemForm()
    
    context = {
        'form': form,
        'today': date.today(),
    }
    return render(request, 'lostfound/report_found.html', context)

@login_required
def item_detail_view(request, item_id, item_type):
    """View details of a specific lost or found item"""
    if item_type == 'lost':
        item = get_object_or_404(LostItem, id=item_id)
    else:
        item = get_object_or_404(FoundItem, id=item_id)
    
    context = {
        'item': item,
        'type': item_type,
    }
    return render(request, 'lostfound/item_detail.html', context)