try:
    with open('source_debug.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('source_log_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Converted source_debug.txt")
except Exception as e:
    print(f"Error source: {e}")

try:
    with open('scrape_debug.txt', 'r', encoding='utf-16') as f: # PowerShell redirection often utf-16
        content = f.read()
    with open('scrape_log_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Converted scrape_debug.txt")
except:
    try:
        with open('scrape_debug.txt', 'r', encoding='utf-8') as f: # Try utf-8 if not utf-16
            content = f.read()
        with open('scrape_log_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Copy scrape_debug.txt (was utf8)")
    except Exception as e:
        print(f"Error scrape: {e}")

try:
    with open('pip_list.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('pip_list_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('pip_list.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('pip_list_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error pip_list: {e}")

try:
    with open('python_path.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('python_path_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('python_path.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('python_path_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error python_path: {e}")

try:
    with open('import_log.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('import_log_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('import_log.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('import_log_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error import_log: {e}")

try:
    with open('import_log_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('import_log_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('import_log_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('import_log_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error import_log_2: {e}")

try:
    with open('posts_count.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('posts_count_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('posts_count.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('posts_count_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error posts_count: {e}")

try:
    with open('scrape_debug_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('scrape_log_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('scrape_debug_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('scrape_log_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error scrape_log_2: {e}")

try:
    with open('scrape_debug_3.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('scrape_log_3_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('scrape_debug_3.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('scrape_log_3_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error scrape_log_3: {e}")

try:
    with open('post_count_check.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('post_count_check_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('post_count_check.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('post_count_check_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error post_count_check: {e}")

try:
    with open('scrape_debug_playwright.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('scrape_debug_playwright_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('scrape_debug_playwright.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('scrape_debug_playwright_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error scrape_debug_playwright: {e}")

try:
    with open('log.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log.txt: {e}")

try:
    with open('log_u.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_u_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_u.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_u_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_u.txt: {e}")

try:
    with open('post_count_check_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('post_count_check_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('post_count_check_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('post_count_check_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error post_count_check_2: {e}")

try:
    with open('log_u_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_u_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_u_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_u_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_u_2.txt: {e}")

try:
    with open('post_count_check_3.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('post_count_check_3_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('post_count_check_3.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('post_count_check_3_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error post_count_check_3: {e}")

try:
    with open('test_pw_log.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('test_pw_log_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('test_pw_log.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('test_pw_log_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error test_pw_log.txt: {e}")

try:
    with open('log_u_3.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_u_3_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_u_3.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_u_3_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_u_3.txt: {e}")

try:
    with open('log_u_4.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_u_4_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_u_4.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_u_4_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_u_4.txt: {e}")

try:
    with open('post_count_final_check.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('post_count_final_check_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('post_count_final_check.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('post_count_final_check_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error post_count_final_check: {e}")

try:
    with open('log_final_debug.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_final_debug_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_final_debug.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_final_debug_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_final_debug.txt: {e}")

try:
    with open('sources_list.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('sources_list_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('sources_list.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('sources_list_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error sources_list.txt: {e}")

try:
    with open('log_reuters_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_reuters_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_reuters_2.txt: {e}")

try:
    with open('log_reuters_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_reuters_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_reuters_2.txt: {e}")

try:
    with open('log_reuters_2.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except:
     try:
        with open('log_reuters_2.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('log_reuters_2_utf8.txt', 'w', encoding='utf-8') as f:
            f.write(content)
     except Exception as e:
        print(f"Error log_reuters_2.txt: {e}")
