import { Resolvers } from '../generated/graphql';
import { Context } from '../../context';
import {
  getPersonById,
  searchPersons,
  getCompanyById,
  searchCompanies,
  getVehicleById,
  searchVehicles,
  getJobById,
  listJobs,
  getProxyStats,
  startCrawlJob,
  startScrapeJob,
  upsertTemplate,
  activateTemplate
} from '../../services';

const resolvers: Resolvers<Context> = {
  Query: {
    person: async (_, { id }, ctx) => {
      return getPersonById(id, ctx);
    },
    persons: async (_, { filter, pagination, sort }, ctx) => {
      return searchPersons(filter, pagination, sort, ctx);
    },
    company: async (_, { id }, ctx) => {
      return getCompanyById(id, ctx);
    },
    companies: async (_, { filter, pagination, sort }, ctx) => {
      return searchCompanies(filter, pagination, sort, ctx);
    },
    vehicle: async (_, { id }, ctx) => {
      return getVehicleById(id, ctx);
    },
    vehicles: async (_, { filter, pagination, sort }, ctx) => {
      return searchVehicles(filter, pagination, sort, ctx);
    },
    job: async (_, { id }, ctx) => {
      return getJobById(id, ctx);
    },
    jobs: async (_, { filter, pagination, sort }, ctx) => {
      return listJobs(filter, pagination, sort, ctx);
    },
    proxyStats: async (_, __, ctx) => {
      return getProxyStats(ctx);
    }
  },

  Mutation: {
    startCrawlJob: async (_, { input }, ctx) => {
      return startCrawlJob(input, ctx);
    },
    startScrapeJob: async (_, { input }, ctx) => {
      return startScrapeJob(input, ctx);
    },
    upsertTemplate: async (_, { input }, ctx) => {
      return upsertTemplate(input, ctx);
    },
    activateTemplate: async (_, { input }, ctx) => {
      return activateTemplate(input, ctx);
    }
  },

  Person: {
    addresses: async (person, { first, after }, ctx) => {
      return getPersonAddresses(person.person_id, first, after, ctx);
    },
    // ... other Person field resolvers ...
  },

  // ... other type resolvers ...
};

export default resolvers;