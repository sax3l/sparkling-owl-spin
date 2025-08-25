import { rule, shield, and, or, not } from 'graphql-shield';

const isAuthenticated = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => {
    return ctx.user !== undefined;
  }
);

const isAdmin = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => {
    return ctx.user?.roles.includes('ADMIN') ?? false;
  }
);

const isAnalyst = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => {
    return ctx.user?.roles.includes('ANALYST') ?? false;
  }
);

export const permissions = shield({
  Query: {
    person: isAuthenticated,
    persons: isAuthenticated,
    company: isAuthenticated,
    companies: isAuthenticated,
    vehicle: isAuthenticated,
    vehicles: isAuthenticated,
    job: isAdmin,
    jobs: isAdmin,
    proxyStats: isAdmin,
  },
  Mutation: {
    '*': isAdmin,
  },
  Person: {
    personal_number: isAdmin,
    maskedPersonalNumber: or(isAdmin, isAnalyst),
    salary: isAdmin,
  },
}, {
  fallbackRule: isAuthenticated,
  allowExternalErrors: process.env.NODE_ENV === 'development',
});