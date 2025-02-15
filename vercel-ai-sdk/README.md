# moremem0 AI SDK Provider
This is a modified version of the offical Mem0 AI SDK Provider.

## Initialization
1. install packages: `pnpm install`
2. set your api_key: modify `.env.example` file and rename it to `.env`

## Run Tests
1. Through nodemon:
  - check the test file path in `nodemon.json`
  - check the content in the file you set above. Here I set it as `example/index.ts`
  - run `pnpm dev`

2. Through jest
  - check the configuration in file `config/test-config.ts`
  - check the files in `tests` folder
  - tests all: `pnpm test`; tests specific file: `pnpm test ./tests/memory-core.test.ts`

## Develop
In the `src` folder is all the source code. You can modify it and run tests.👆