#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import cgi
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

    def get_posts(limit, offset):
        entries = db.GqlQuery("SELECT * FROM Entries ORDER BY created DESC LIMIT 5 OFFSET '%s'" % offset)

class Entries(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", entry="", error=""):
        self.render("front.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('title')
        entry = self.request.get('entry')

        if title and entry:
            a = Entries(title = title, entry = entry)
            a.put()

            id = a.key().id()
            self.redirect("/blog/" + str(id))

        else:
            error = "We need both a title and some content!"
            self.render_front(title, entry, error)

class NewPost(Handler):
    def render_front(self, title="", entry="", error=""):
        self.render("front.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('title')
        entry = self.request.get('entry')

        if title and entry:
            a = Entries(title = title, entry = entry)
            a.put()

            id = a.key().id()
            self.redirect("/blog/" + str(id))

        else:
            error = "We need both a title and some content!"
            self.render_front(title, entry, error)

class BlogPage(Handler):
    def render_blog(self, title="", entry=""):
        entries = db.GqlQuery("SELECT * FROM Entries " "ORDER BY created DESC LIMIT 5 ")
        self.render("blog-submissions.html", title=title, entry=entry, entries=entries)

    def get(self):
        title = self.request.get('title')
        entry = self.request.get('entry')


        self.render_blog(title, entry)

class ViewPostHandler(Handler):
    def render_perma(self, title="", entry="", error=""):
        self.render("permalink.html", title=title, entry=entry, error=error)

    def get(self, id):

        entry = db.GqlQuery("SELECT * FROM Entries WHERE ID = 'id'")
        blogpost = Entries.get_by_id(int(id))

        if blogpost:
            title = blogpost.title
            entry = blogpost.entry
            created = blogpost.created

            t = jinja_env.get_template("permalink.html")
            content = t.render(blogpost = blogpost, title = title, entry = entry, created = created)
            self.response.write(content)
        else:
            error = "I'm sorry but it seems that post does not exist"
            self.render_perma(error)




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
