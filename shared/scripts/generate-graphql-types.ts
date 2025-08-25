import { generate } from '@graphql-codegen/cli';
import { join } from 'path';

async function main() {
  await generate({
    schema: join(__dirname, '../docs/graphql/schema.graphql'),
    generates: {
      [join(__dirname, '../src/graphql/generated/graphql.ts')]: {
        plugins: [
          'typescript',
          'typescript-resolvers',
          'typescript-operations',
        ],
        config: {
          contextType: '../context#Context',
          useIndexSignature: true,
          strictScalars: true,
          scalars: {
            DateTime: 'Date',
            Decimal: 'number',
            JSON: 'any',
          },
        },
      },
    },
  });
}

main().catch(console.error);