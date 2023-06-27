import re

def on_page_content(html: str, **kwargs) -> str:
    
    # Fix plots in jupyter notebook
    html = re.sub('(?<=<script type="text\/javascript">)\s*?require\(\["plotly"\], function\(Plotly\) {\s*?(?=window\.PLOTLYENV)', "", html)
    html = re.sub('\).then\(function\(\){.*?(?=<\/script>)', ')}', html, flags=re.S)    
    return html