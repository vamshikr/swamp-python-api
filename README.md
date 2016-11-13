# swamp-python-api
Python API to access SWAMP (unofficial)

Currently, the API supports uploading and assessment of *Java* packages in SWAMP. Support for other languages will be added soon.

## Build
To build and install, execute `python setup install` in your python environment. This command installs a package `swamp_api` and creates an executable script by the name `swamp-api` in your python environment.

### API
The API methods are in the package `swamp_api`. If you plan to use this from another program, import the API using the statement `from swamp_api import SwampApi`. The `SwampApi` object has methods to perform the following tasks
1. login
2. get project list
3. get package list
4. upload a package
5. get package types
6. get supported platforms
7. get tools
8. assess a package*.

### CLI
`swamp-api` is a command line program to access SWAMP. Run `swamp-api --help` for help.

`swamp-api` has the following *commands*:

| Command | Description |
| --- | --- |
| login          | login into SWAMP |
|    projects          |  Get the list of projects that you own |
|    packages          |  Get the list of package for a project |
|    upload            |  Upload a Java package |
|    package-types     |  Get package types |
|    platforms         |  Get platforms list |
|    tools             |  Get tools list |
|    assess            |  Run assessments |
|    execution-records |   Get execution records for the project |


## CLI Usage Examples

#### Login
```
swamp-api login --help

swamp-api login --user-info-file ~/appdev/user-info.conf
```

#### Projects
```
# swamp-api projects [-h] --user-uuid SWAMP_USER_UUID
swamp-api projects --user-uuid 707151BD-F9F5-4B43-8E24-CAB4325C02BC

```

#### Packages
```
# swamp-api packages [-h] --project-uuid PROJECT_UUID [--with-versions]
swamp-api packages --project-uuid 707151BD-F9F5-4B43-8E24-CAB4325C02BC

```

#### Upload Package
```
swamp-api upload  \
    --archive ~/package/webgoat-5.4/webgoat-5.4.zip \
    --pkg-conf  ~/package/webgoat-5.4/package.conf \
    --user-uuid BC773958-A790-442C-8FBF-5E846C0A3C83 \
    --project-uuid B6FA650A-2044-452F-86E1-1E5E8EA6164D \
    [--package-uuid SWAMP_PACKAGE_UUID]]
```

#### Tools
```
swamp-api tools --public

swamp-api tools --restricted
```

#### Platforms
```
swamp-api platforms
```

#### Assess a package

```
swamp-api assess \
    --project-uuid 707151BD-F9F5-4B43-8E24-CAB4325C02BC \
    --package-uuid DCD8E716-51CB-4E84-B2DA-7AF7A09719F2 \
    --package-version-uuid C5BC13F5-1A66-4D9B-8BF3-2B93BAE86A93 \
    --tool-uuid 163d56a7-156e-11e3-a239-001a4a81450 \
    --plat-uuid 1088c3ce-20aa-11e3-9a3e-001a4a81450b \
    --notify-when-complete  # SWAMP will send you an email
```
