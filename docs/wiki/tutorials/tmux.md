## Creating tmux session

```
JS-NG>session = j.core.executors.tmux.create_session("watching system processes")
```

## Creating a window inside session

```
JS-NG> session.new_window()                                                              
Window(@1 1:zsh, Session($0 ps))
```
## Get or create js session
```
JS-NG> js_session = j.core.executors.tmux.get_js_session()
```
## Get or create js window `A window from js session`
```
JS-NG> js_window = j.core.executors.tmux.get_js_window("window_name")
```
## Get window `if it exists, if not it will create it in a js session`
```
JS-NG> window = j.core.executors.tmux.get_window("window_name")
```
## Executing a command in a window
```
JS-NG> j.core.executors.tmux.execute_in_window("ls", window_name)

```