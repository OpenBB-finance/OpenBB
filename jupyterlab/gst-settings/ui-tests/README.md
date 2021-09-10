# Test

The test will produce a video to help debugging and check what happened.

To execute integration tests, you have two options:

- use docker-compose (cons: needs to know and use docker) - this is a more reliable solution.
- run tests locally (cons: will interact with your JupyterLab user settings)

## Test on docker

1. Compile the extension:

```
jlpm install
jlpm run build:prod
```

2. Execute the docker stack in the example folder:

```
docker-compose -f ../end-to-end-tests/docker-compose.yml --env-file ./ui-tests/.env build
docker-compose -f ../end-to-end-tests/docker-compose.yml --env-file ./ui-tests/.env run --rm e2e
docker-compose -f ../end-to-end-tests/docker-compose.yml --env-file ./ui-tests/.env down
```

## Test locally

1. Compile the extension:

```
jlpm install
jlpm run build:prod
```

2. Start JupyterLab _with the extension installed_ without any token or password

```
jupyter lab --ServerApp.token= --ServerApp.password=
```

3. Execute in another console the [Playwright](https://playwright.dev/docs/intro) tests:

```
cd ui-tests
jlpm install
npx playwright install
npx playwright test
```

# Create tests

To create tests, the easiest way is to use the code generator tool of playwright:

1. Compile the extension:

```
jlpm install
jlpm run build:prod
```

2. Start JupyterLab _with the extension installed_ without any token or password:

**Using docker**

```
docker-compose -f ../end-to-end-tests/docker-compose.yml --env-file ./ui-tests/.env run --rm -p 8888:8888 lab
```

**Using local installation**

```
jupyter lab --ServerApp.token= --ServerApp.password=
```

3. Launch the code generator tool:

```
cd ui-tests
jlpm install
npx playwright install
npx playwright codegen localhost:8888
```

# Debug tests

To debug tests, a good way is to use the inspector tool of playwright:

1. Compile the extension:

```
jlpm install
jlpm run build:prod
```

2. Start JupyterLab _with the extension installed_ without any token or password:

**Using docker**

```
docker-compose -f ../end-to-end-tests/docker-compose.yml --env-file ./ui-tests/.env run --rm -p 8888:8888 lab
```

**Using local installation**

```
jupyter lab --ServerApp.token= --ServerApp.password=
```

3. Launch the code generator tool:

```
cd ui-tests
jlpm install
npx playwright install
PWDEBUG=1 npx playwright test
```
