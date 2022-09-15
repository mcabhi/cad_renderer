from bottle import run, request, static_file, post

from draw import Canvas


@post('/cad')
def index():
    canvas = Canvas(request.json)
    canvas.draw()

    filename = 'example.svg'
    return static_file(filename, root='/tmp', download=filename)

run(host='0.0.0.0', port=5001)
