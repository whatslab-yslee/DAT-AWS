from streamlit_js_eval import get_cookie, set_cookie, streamlit_js_eval


def get_browser_cookie(key: str, component_key=None):
    return get_cookie(key, component_key)


def set_browser_cookie(key: str, value: str, duration_days: int, component_key=None):
    set_cookie(key, value, duration_days, component_key)
    return True


def delete_browser_cookie(key: str, component_key=None):
    js_ex = f"document.cookie = '{key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; Max-Age=0; path=/;'"
    if component_key is None:
        component_key = js_ex
    streamlit_js_eval(js_expressions=js_ex, key=component_key)
    return True


def set_item_local_storage(key: str, value: str, component_key=None):
    js_ex = f"localStorage.setItem('{key}', '{value}')"
    if component_key is None:
        component_key = js_ex
    streamlit_js_eval(js_expressions=js_ex, key=component_key)
    return True


def get_item_local_storage(key: str, component_key=None):
    js_ex = f"localStorage.getItem('{key}')"
    if component_key is None:
        component_key = js_ex
    return streamlit_js_eval(js_expressions=js_ex, key=component_key)


def remove_item_local_storage(key: str, component_key=None):
    js_ex = f"localStorage.removeItem('{key}')"
    if component_key is None:
        component_key = js_ex
    streamlit_js_eval(js_expressions=js_ex, key=component_key)
    return True
