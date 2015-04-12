import asyncio
import json


class Http:

    def __init__(self,ip,**kargs):
        self.ip = ip
        self.header = {
            Host:self.ip,
            Content-Type:"text/html; charset=utf-8",
            Accept:"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            Accept-Language: "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            Accept-Encoding: "gzip, deflate",


        }
        

        


    @asyncio.coroutine
    def write_header(self,writer):
        for k,v in self.header:
            writer.write((k+': '+v+'\r\n').encode())
        writer.write(b'\r\n')
        yield from writer.drain()

    @asyncio.coroutine
    def read_header(reader):
        response_headers = {}
        while True:
            line_bytes = yield from reader.readline()
            line = line_bytes.decode().strip()
            if not line:
                break
            key, value = line.split(':', 1)
            response_headers[key.strip()] = value.strip()
        return response_headers

    @asyncio.coroutine
    def request(self,host,path):
        reader, writer = yield from asyncio.open_connection(host, 80)
        paths = 'GET %s HTTP/1.1\r\n'%(path)
        writer.write(paths.encode())
        yield from self.write_headers(writer)
        status_line = yield from self.reader.readline()
        status_line = status_line.decode().strip()
        http_version, status_code, status = status_line.split(' ')
        if verbose:
            print('Got status {} {}'.format(status_code, status))
        response_headers = yield from read_headers(reader)
        if verbose:
            print('Response headers:')
            for key, value in response_headers.items():
                print(key + ': ' + value)
        # Assume the content length is sent by the server, which is the case
        # with ipify
        content_length = int(response_headers['Content-Length'])
        response_body_bytes = yield from reader.read(content_length)
        response_body = response_body_bytes.decode()
        response_object = json.loads(response_body)
        writer.close()
        return response_object['ip']