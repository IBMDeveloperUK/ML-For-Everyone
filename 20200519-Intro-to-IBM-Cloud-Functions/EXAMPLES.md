A simple hello world function
```
% cat hello.py
def main(args):
    name = args.get("name", "unknown")
    return {"message": f"Hello {name}!"}
```

create an action
```
% ic fn action create hello hello.py
ok: created action hello
```

list actions
```
% ic fn action list                             
actions
/Matthew.Hamilton1@ibm.com_dev/hello                                   private python:3.7
```

invoke a function
```
% ic fn action invoke hello -r
{
    "message": "Hello unknown!"
}
```

Update a function
```
% ic fn action update hello hello.py
ok: updated action hello
```

# Delete a function
```
% ic fn action delete hello         
ok: deleted action hello
```
