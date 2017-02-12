
import webapp2
import jinja2
import os
import cgi
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))




class BlogPost(db.Model):
    title = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)
    body = db.StringProperty(required= True)

def get_posts(limit, offset):
    limit = limit
    offset = offset
    query = BlogPost.all().order("-created")
    recent_blogs = query.fetch(offset=offset, limit=limit)
    return recent_blogs


class Handler(webapp2.RequestHandler):
    def renderError(self,error_code):
        self.error(error_code)
        self.response.write("oops something went wrong")



class BlogHandler(webapp2.RequestHandler):
    def get(self):
        page =self.request.get("page")
        blogTotal = BlogPost.all(keys_only=True).count()
        if page:
            page = int(page)
        else:
            page=1
        nextPage=page+1
        prevPage=page-1
        recent_blogs = get_posts(5,((page-1)*5))
        morePages =True
        if blogTotal - page*5 < 1:
            morePages = False





        ##recent_blogs = get_posts(5,0)
        ##query = BlogPost.all().order("-created")
        ##recent_blogs = query.fetch(limit = 5)
        t = jinja_env.get_template("blog.html")



        content = t.render(blogs = recent_blogs, page=page,nextPage=nextPage, prevPage=prevPage, morePages=morePages)
        self.response.write(content)

class newPostHandler(webapp2.RequestHandler):
    def renderPage(self, title="",body="", error=""):
        t = jinja_env.get_template("newpost.html")
        content = t.render(title = title, error=error, body=body)
        self.response.write(content)


    def get(self):
        self.renderPage()
    def post(self):
        new_post_title = self.request.get("title")
        new_post_body = self.request.get("body")
        if (not new_post_body) or (not new_post_title) or (new_post_body.strip()=="") or (new_post_title.strip() == ""):
            error = "Please add a body and title"
            self.renderPage(title=new_post_title, body=new_post_body, error=error)
            return
        new_post_body_escaped = cgi.escape(new_post_body, quote=True)
        new_post_title_escaped = cgi.escape(new_post_title, quote=True)
        post = BlogPost(title=new_post_title_escaped, body = new_post_body_escaped )
        post.put()
        postid = post.key().id()



        ## change this later to go to BlogPost
        self.redirect("/blog/"+str(postid))





class ViewPostHandler(webapp2.RequestHandler):
    def get(self,id):
        post = BlogPost.get_by_id(int(id))
        t = jinja_env.get_template("blogpost.html")
        content = t.render(post=post)


        self.response.write(content)







app = webapp2.WSGIApplication([
    ('/', BlogHandler),
    ('/newpost',newPostHandler),
    ('/blog', BlogHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)


], debug=True)
