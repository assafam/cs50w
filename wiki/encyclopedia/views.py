from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util
from . import markdown
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    if util.get_entry(entry) is None:
        return render(request, "encyclopedia/entry.html", {
            "entry": "Not Found",
            "content": f"<div class=\"alert alert-danger\">Entry \"{entry}\" not found</div>"
        })

    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "content": markdown.markdown(util.get_entry(entry))
    })

def search(request):
    term = request.GET.get('q')
    if term in util.list_entries():
        return HttpResponseRedirect(reverse("encyclopedia:wiki", args=[term]))

    results = filter(lambda entry: term.lower() in entry.lower(), util.list_entries())
    return render(request, "encyclopedia/search.html", {
        "entries": sorted(results)
    })

def random_entry(request):
    term = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("encyclopedia:wiki", args=[term]))

def new(request):
    error_exists = ""
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if title in util.list_entries():
                error_exists = "<div class=\"alert alert-danger\">Error! Entry already exists</div>"
            else:
                util.save_entry(title, form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("encyclopedia:wiki", args=[title]))
    else:
        form = NewEntryForm()

    return render(request, "encyclopedia/new.html", {
        "form": form,
        "error_exists": error_exists
    })


def edit(request, entry):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            util.save_entry(entry, form.cleaned_data["content"])
            return HttpResponseRedirect(reverse("encyclopedia:wiki", args=[entry]))
    else:
        form = EditForm(initial={"content": util.get_entry(entry)})

    return render(request, "encyclopedia/edit.html", {
        "entry": entry,
        "form": form
    })

class NewEntryForm(forms.Form):
    title = forms.SlugField()
    content = forms.CharField(required=False, widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(required=False, widget=forms.Textarea)
