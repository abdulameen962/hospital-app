from waitress import serve


from capstone.wsgi import application

if __name__ == '__main__':
    serve(application,listen='*:8080')
