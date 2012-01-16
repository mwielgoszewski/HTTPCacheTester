#!/usr/bin/env python
import cherrypy

FORMATS = {
 'pdf':  'application/pdf',
 'doc':  'application/msword',
 'xls':  'application/vnd.excel',
 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
 'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.document',
}


class HTTPCacheTester(object):

    @cherrypy.expose
    def index(self):
        outfile = open('download.html', 'rb')
        return file2Generator(outfile)

    @cherrypy.expose
    def download(self,
                 public=None,
                 private=None,
                 nocache=None,
                 nostore=None,
                 notransform=None,
                 mustrevalidate=None,
                 maxage=None,
                 pragma=None,
                 expires=None,
                 disposition='inline',
                 format='pdf'):

        resp = cherrypy.response

        format = format.lower().strip()
        disposition = 'inline' if disposition == 'inline' else 'attachment'

        cache_control = []

        if public == 'on':
            cherrypy.log("Setting Cache-Control: public")
            cache_control.append('public')

        if private == 'on':
            cherrypy.log("Setting Cache-Control: private")
            cache_control.append('private')

        if nocache == 'on':
            cherrypy.log("Setting Cache-Control: no-cache")
            cache_control.append('no-cache')

        if nostore == 'on':
            cherrypy.log("Setting Cache-Control: no-store")
            cache_control.append('no-store')

        if notransform == 'on':
            cherrypy.log("Setting Cache-Control: no-transform")
            cache_control.append('no-transform')

        if mustrevalidate == 'on':
            cherrypy.log("Setting Cache-Control: must-revalidate")
            cache_control.append('must-revalidate')

        if maxage is not None and maxage.strip().isidigit():
            maxage = int(maxage.strip())
            cherrypy.log("Setting Cache-Control: max-age=%d" % (maxage, ))
            cache_control.append('max-age=%d' % (maxage, ))

        if pragma == 'on':
            cherrypy.log("Setting Pragma: no-cache")
            resp.headers['Pragma'] = 'no-cache'

        if cache_control:
            resp.headers['Cache-Control'] = ', '.join(cache_control)

        if expires is not None:
            expires = parse_expires(expires)
            cherrypy.log("Setting Expires: %r" % (expires, ))
            resp.headers['Expires'] = expires

        if format in FORMATS:
            resp.headers['Content-Type'] = FORMATS.get(format, 'pdf')

            filename = "test.%s" % (format, )

            cherrypy.log("Setting Content-Disposition: %s; filename=%s" % (
                disposition, filename))

            resp.headers['Content-Disposition'] = "%s; filename=%s" % (
                disposition, filename)

            outfile = open(filename, 'rb')
            return file2Generator(outfile)
        else:
            outfile = open('download.html', 'rb')
            return file2Generator(outfile)


def file2Generator(f):
    try:
        while True:
            data = f.read(1024 * 8)
            if not data:
                break

            yield data
    finally:
        cherrypy.log("Closing open file %r" % (f, ))
        f.close()


def parse_expires(value):
    try:
        return int(value)
    except TypeError:
        return value.replace('\r', '').replace('\n', '').strip()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser('HTTPCacheTester')
    parser.add_option('-c', '--config',
                      help="Filename of a cherrypy file configuration",
                      default=None)

    opt, args = parser.parse_args()

    cherrypy.quickstart(HTTPCacheTester(), config=opt.config)

