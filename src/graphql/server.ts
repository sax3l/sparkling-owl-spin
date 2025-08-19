import { ApolloServer } from 'apollo-server-express';
import { applyMiddleware } from 'graphql-middleware';
import { makeExecutableSchema } from '@graphql-tools/schema';
import { typeDefs } from './schema';
import resolvers from './resolvers';
import { context } from './context';
import { permissions } from './permissions';
import { formatError } from './errorFormatter';
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const schema = makeExecutableSchema({ typeDefs, resolvers });

const schemaWithMiddleware = applyMiddleware(
  schema,
  permissions
);

const validationRules = [
  depthLimit(10),
  createComplexityLimitRule(1000, {
    onCost: (cost) => {
      console.log(`Query cost: ${cost}`);
    },
  })
];

export const server = new ApolloServer({
  schema: schemaWithMiddleware,
  context,
  formatError,
  validationRules,
  introspection: process.env.NODE_ENV !== 'production',
  plugins: [
    {
      requestDidStart() {
        return {
          didResolveOperation({ request, document }) {
            // Log query complexity analysis
            const complexity = getComplexity({
              schema,
              operationName: request.operationName,
              query: document,
              variables: request.variables,
            });
            console.log(`Query complexity: ${complexity}`);
          },
        };
      },
    },
  ],
});

// Apply to Express app
export const applyGraphQLMiddleware = (app) => {
  server.start().then(() => {
    server.applyMiddleware({ app, path: '/graphql' });
  });
};