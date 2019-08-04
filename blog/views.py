from django.shortcuts import render
from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
#from ibm_watson import ToneAnalyzerV3

import requests
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3

language_translator = LanguageTranslatorV3(
        version='2018-05-31',
        iam_apikey='PckvhDE1FkqfzN8ajFYoRa_RUSE8otYsnNrJGR_hzey_')


tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='2h8D2iJJPfigBXh76q7d0V1YJgvaGM7_ItHXx6INYBJA',
)


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation = language_translator.translate(
            text=post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        # print(obj)
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']
        tone_input = ToneInput(post.text)
        tone = tone_analyzer.tone(tone_input=tone_input, content_type="application/json")
        tone2 = str(tone)
        tone2_data = json.loads(tone2)
        json_data = tone2_data['result'].get('document_tone').get('tones')
        tone_name = 'Not Found'
        tone_score = 'Not Found'
        for tone_id in json_data:
            tone_name = tone_id.get('tone_name')
            tone_score = tone_id.get('score')
        post.tone_name = tone_name
        post.tone_score = tone_score
        post.tone3 = tone2_data['result'].get('sentences_tone')
        print(post.tone3)
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})