import json,html
from pathlib import Path

def main():
 md=Path("gazette/latest.md").read_text(encoding="utf-8") if Path("gazette/latest.md").exists() else "# Bago Block Gazette\nAwaiting first ESPN collection."
 lines=md.splitlines(); body=[]
 for x in lines:
  if x.startswith("# "): body.append(f"<h1>{html.escape(x[2:])}</h1>")
  elif x.startswith("## "): body.append(f"<h2>{html.escape(x[3:])}</h2>")
  elif x.startswith("- "): body.append(f"<p class='item'>{html.escape(x[2:])}</p>")
  elif x.startswith("*") and x.endswith("*"): body.append(f"<p class='deck'>{html.escape(x.strip('*'))}</p>")
  elif x and x!="---": body.append(f"<p>{html.escape(x)}</p>")
 page="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Bago Block Gazette</title><style>
 body{max-width:980px;margin:auto;padding:28px;background:#eee9dc;color:#171717;font-family:Georgia,serif}
 header{text-align:center;border-top:8px solid #111;border-bottom:3px double #111;padding:12px} .brand{font-size:3rem;font-weight:900}
 main{background:#f8f4e8;padding:30px;box-shadow:0 2px 16px #999} h1{font-size:2.2rem;border-bottom:2px solid #111;padding-bottom:10px} h2{font-family:Arial,sans-serif;text-transform:uppercase;border-bottom:1px solid #555;margin-top:32px}
 .item{font-size:1.1rem;border-bottom:1px dotted #999;padding:9px 0}.deck{font-style:italic;color:#555} footer{text-align:center;font:12px Arial;margin:24px}
 </style></head><body><header><div class="brand">THE BAGO BLOCK GAZETTE</div><div>Fantasy Football's Least Reliable Newspaper</div></header><main>"""+''.join(body)+"""</main><footer>Automated from Bago Block v3 league data</footer></body></html>"""
 Path("site").mkdir(exist_ok=True); Path("site/index.html").write_text(page,encoding="utf-8")
if __name__=="__main__":main()
