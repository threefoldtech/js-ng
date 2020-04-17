# Using System Fs

Manipulating filesystem is one of the most common things in the daily life of a developer, administrator, .. etc. js-ng comes with tons of helpers and utilities around that in `j.sals.fs`. You will find the module already self documented with lots of examples in each function.


### Get current working dir

```
> j.sals.fs.cwd()
'/home/xmonader/wspace/js-next/js-ng'
```

### Get basename
```
> j.sals.fs.basename(j.sals.fs.cwd()) 
'js-ng'
```

### Get Dir name
```
> j.sals.fs.dirname(j.sals.fs.cwd())
'/home/xmonader/wspace/js-next'
> j.sals.fs.parent(j.sals.fs.cwd()) 
'/home/xmonader/wspace/js-next'
```

### is dir

```
> j.sals.fs.is_dir(path= '/home/rafy')
True
```
### is file
```
> j.sals.fs.is_file(path= '/home/rafy')
False
```

### is ascii file

```
> j.sals.fs.is_ascii_file(path="/home/rafy/testfile")
True
```

### Is absolute path

```
> j.sals.fs.is_absolute('/home/rafy/')
True
```

### Check if empty dir
```
> j.sals.fs.is_empty_dir("/home/rafy/empty_dir")
True
```

### File paths exists or not

```
> j.sals.fs.exists("/home/rafy/testing_make_dir/test1")
True
```

## Reading/Writing to a file

There're some helpers around reading/writing text, binary like `read_text`, `read_binary`, `read_file`, `write_text`, `write_binary`, `touch`

### Touching a new file

```
> j.sals.fs.touch("/home/rafy/testing_touch")
```

### Reading a text

```
> j.sals.fs.read_text("/home/rafy/testing_text.txt")
'hello world\n'

```

### Reading binary

```
> j.sals.fs.read_bytes("/home/rafy/testing_text.txt")
b'hello world\n'
```


### Writing text

```
> j.sals.fs.write_text(path="/home/rafy/testing_text.txt",data="hello world")
11
```

### Writing binary

```
> j.sals.fs.write_bytes(path="/home/rafy/testing_text.txt",data=b"hello world")
11
```


rename, move, copy_file, copy_tree, mkdir, mkdirs, join_paths, , rmtree, rm_empty_dir, symlink, chmod, chown, basename, dirname, normalizing paths, expanding `~`



### Making directories
```
> j.sals.fs.mkdirs("/home/rafy/testing_make_dir/test1/test2",exist_ok=False)
```
will raise if in case the directory already exists

```
> j.sals.fs.mkdirs("/home/rafy/testing_make_dir/test1/test2",exist_ok=True) 
```
Won't raise if the directory exists

### Get the stem of the filepath

```
> j.sals.fs.stem("/tmp/tmp-5383p1GOmMOOwvfi.tpl") 'tmp-5383p1GOmMOOwvfi'
   
```

### Get the parent 

```
> j.sals.fs.parent("/home/rafy/testing_make_dir/test1")
'/home/rafy/testing_make_dir'
```

### Get parents

```
> j.sals.fs.parents("/tmp/home/ahmed/myfile.py")
    [PosixPath('/tmp/home/ahmed'),
    PosixPath('/tmp/home'),
    PosixPath('/tmp'),
    PosixPath('/')]
```


### Rename file
```
> j.sals.fs.rename("/home/rafy/testing_make_dir","/home/rafy/testing_dir") 
```

### Expand user
```
> j.sals.fs.expanduser("~/work")
'/home/xmonader/work'
```

### Get temporary filename 
```
> j.sals.fs.get_temp_filename(dir="/home/rafy/")  
'/home/rafy/tmp6x7w71ml'
```

```
> j.sals.fs.get_temp_dirname(dir="/home/rafy")  
'/home/rafy/tmpntm2ptqy'
```

```
> j.sals.fs.join_paths("home","rafy")  
'home/rafy'
```

### Resolving a path
```
> j.sals.fs.resolve("")  
PosixPath('/home/rafy/Documents')
> j.sals.fs.resolve("./testing_text.txt")  
PosixPath('/home/rafy/Documents/testing_text.txt')
```

## Walkers
It's very common to walk on the filesystem and filtering based on some properties of the path 
And very fancy walkers

### Walk over on files only

```
for el in walk('/tmp', filter_fun=j.sals.fs.is_file) : ..
```
or more specific function walk_files

```
for el in walk_files('/tmp') : ..
```



### Walk over on dirs only

```
for el in walk('/tmp', filter_fun=j.sals.fs.is_dir) : ..
```
or more specific function `walk_dirs`

```
for el in walk_dirs('/tmp') : ..

```

### walk over with a bit complex filter

 Walk over paths that are files or dirs and longer than 4 characters in the name

```
for el in walk('/tmp', filter_fun= lambda x: len(x)>4 and (j.sals.fs.is_file(x) or j.sals.fs.is_dir(x)) ) : ..
```
   

There are more functionality available in the SAL `j.sals.fs` make sure you check the API documentation for more.
