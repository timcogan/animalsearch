# animalsearch

A commandline tool for finding animals in pictures.

## How to use

Open a terimal to install using pip:
```
$ pip install animalsearch
```

Run the tool on a folder containing only images:
```
$ animalsearch PATH_TO_IMAGE_FOLDER --mode sort
```

The folder should be structured like this:
```
PATH_TO_IMAGE_FOLDER/
    img000.jpg
    img001.jpg
    ...
    imgXXX.jpg
```

If there are any non-image files or folders in `PATH_TO_IMAGE_FOLDER`, the tool will throw an error message.
This is a safety mechanism.

Once the tool is run, your folder should look like this:
```
PATH_TO_IMAGE_FOLDER/
    animals/
        img000.jpg
        img003.jpg
        img004.jpg
        ...
    no_animals/
        img001.jpg
        img002.jpg
        img005.jpg
        ...
```

Read the help menu for more information.
```
$ animalsearch -h
```

## FAQ

For more information about the code in this repo, take a look at the original source
[here](https://github.com/microsoft/CameraTraps).