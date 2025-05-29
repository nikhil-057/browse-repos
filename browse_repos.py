import os
import markdown
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pygments import highlight
from pygments.lexers import PythonLexer, BashLexer
from pygments.formatters import HtmlFormatter

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve files while rendering Markdown as HTML and highlighting .py and .sh files."""
        file_path = self.translate_path(self.path)

        if os.path.isdir(file_path):
            return super().do_GET()

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".md":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                    html_content = markdown.markdown(md_content)
                    self.wfile.write(html_content.encode("utf-8"))
            except Exception:
                self.send_error(404, "File not found")
        elif ext in [".py", ".sh"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    lexer = PythonLexer() if ext == ".py" else BashLexer()
                    highlighted_code = highlight(code, lexer, HtmlFormatter(style="friendly", full=True))
                    self.wfile.write(highlighted_code.encode("utf-8"))
            except Exception:
                self.send_error(404, "File not found")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            try:
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            except Exception:
                self.send_error(404, "File not found")

def run_server(port=8001):
    httpd = HTTPServer(("", port), CustomHandler)
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
