import os
import markdown
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pygments import highlight
from pygments.lexers import PythonLexer, BashLexer
from pygments.formatters import HtmlFormatter

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        rel_path = path.lstrip("/")
        parent_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
        return os.path.join(parent_root, rel_path)

    def do_GET(self):
        file_path = self.translate_path(self.path)
        if os.path.isdir(file_path):
            return self.list_directory(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".md":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                    html_content = markdown.markdown(md_content)
                    self.wfile.write(html_content.encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, "File not found")
            except Exception as e:
                self.send_error(500, f"Internal server error: {str(e)}")

        elif ext in [".py", ".sh"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    lexer = PythonLexer() if ext == ".py" else BashLexer()
                    formatter = HtmlFormatter(style="friendly", full=False)
                    highlighted = highlight(code, lexer, formatter)
                    html = f"""
                        <html><head>
                        <style>{formatter.get_style_defs('.highlight')}</style>
                        </head><body>
                        <pre class="highlight">{highlighted}</pre>
                        </body></html>
                    """
                    self.wfile.write(html.encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, "File not found")
            except Exception as e:
                self.send_error(500, f"Internal server error: {str(e)}")

        else:
            try:
                with open(file_path, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "File not found")
            except Exception as e:
                self.send_error(500, f"Internal server error: {str(e)}")

    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(403, "No permission to list directory")
            return None

        entries.sort()
        r = ["<html><head><title>Directory listing</title></head><body>"]
        r.append(f"<h2>Directory listing for {self.path}</h2><ul>")
        for name in entries:
            fullname = os.path.join(path, name)
            display_name = name + "/" if os.path.isdir(fullname) else name
            link_name = os.path.join(self.path, name).replace("\\", "/")
            r.append(f'<li><a href="{link_name}">{display_name}</a></li>')
        r.append("</ul>")

        readme_path = os.path.join(path, "README.md")
        if os.path.isfile(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    readme_content = markdown.markdown(f.read())
                    r.append("<hr><div>" + readme_content + "</div>")
            except Exception as e:
                r.append(f"<hr><p>Error rendering README.md: {e}</p>")

        r.append("</body></html>")
        encoded = "\n".join(r).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

def run_server(port=8001):
    httpd = HTTPServer(("", port), CustomHandler)
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
