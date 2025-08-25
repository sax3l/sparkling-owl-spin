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
  activateTemplate,
  # New service functions for nested data
  getPersonAddresses,
  getPersonContacts,
  getCompanyFinancials,
  getCompanyRoles,
  getVehicleOwners,
  getVehicleHistory,
} from '../../services'; // Assuming these service functions exist or will be created

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
      // The input type here will be CrawlJobInput from the GraphQL schema
      // You might need to map it to your internal CrawlJobCreate Pydantic model if different
      return startCrawlJob(input, ctx);
    },
    startScrapeJob: async (_, { input }, ctx) => {
      // Similar mapping might be needed for ScrapeJobInput
      return startScrapeJob(input, ctx);
    },
    upsertTemplate: async (_, { input }, ctx) => {
      // Similar mapping might be needed for TemplateInput
      return upsertTemplate(input, ctx);
    },
    activateTemplate: async (_, { templateId, version }, ctx) => {
      return activateTemplate({ templateId, version }, ctx);
    }
  },

  Person: {
    addresses: async (person, { first, after }, ctx) => {
      // Assuming getPersonAddresses returns a connection-like object
      return getPersonAddresses(person.person_id, first, after, ctx);
    },
    contacts: async (person, { first, after }, ctx) => {
      return getPersonContacts(person.person_id, first, after, ctx);
    },
    companies: async (person, { first, after }, ctx) => {
      // This would resolve roles a person has in companies
      // You might need a specific service function like getCompaniesByPersonRole
      return { edges: [], pageInfo: { hasNextPage: false, endCursor: null }, totalCount: 0 }; // TODO: Implement
    },
    vehicles: async (person, { first, after }, ctx) => {
      // This would resolve vehicles a person owns
      // You might need a specific service function like getVehiclesOwnedByPerson
      return { edges: [], pageInfo: { hasNextPage: false, endCursor: null }, totalCount: 0 }; // TODO: Implement
    },
    maskedPersonalNumber: (parent) => {
      // Implement masking logic here, or fetch from a service that provides masked data
      return parent.personal_number ? `***-***-${parent.personal_number.slice(-4)}` : null;
    },
    # Add resolvers for age, salary, remark if they are computed or need special handling
  },

  Company: {
    financials: async (company, { first, after }, ctx) => {
      return getCompanyFinancials(company.company_id, first, after, ctx);
    },
    vehicles: async (company, { first, after }, ctx) => {
      // This would resolve vehicles owned by the company
      return { edges: [], pageInfo: { hasNextPage: false, endCursor: null }, totalCount: 0 }; // TODO: Implement
    },
    roles: async (company, { first, after }, ctx) => {
      return getCompanyRoles(company.company_id, first, after, ctx);
    },
    # Add resolver for annual_reports if needed
  },

  Vehicle: {
    tech_specs: async (vehicle, _, ctx) => {
      // Assuming getVehicleTechnicalSpecs returns a single object or null
      return ctx.loaders.vehicleTechnicalSpecs.load(vehicle.vehicle_id); // TODO: Implement loader
    },
    owners: async (vehicle, { first, after }, ctx) => {
      return getVehicleOwners(vehicle.vehicle_id, first, after, ctx);
    },
    history: async (vehicle, { first, after }, ctx) => {
      return getVehicleHistory(vehicle.vehicle_id, first, after, ctx);
    },
  },

  Job: {
    # Job fields are typically directly mapped from the source object,
    # but if any are computed or nested, they would need resolvers here.
    # progress, metrics, export, logs, links are already handled by the Pydantic model's @model_validator
    # if the source is an ORM object. If the source is a plain object, you might need to map them here.
  },

  # --- Connection Type Resolvers ---
  PersonConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  PersonEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  # Add similar resolvers for all other Connection and Edge types
  CompanyConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  CompanyEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  VehicleConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  VehicleEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  PersonAddressConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  PersonAddressEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  PersonContactConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  PersonContactEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  CompanyFinancialConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  CompanyFinancialEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  CompanyRoleConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  CompanyRoleEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  VehicleOwnershipConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  VehicleOwnershipEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  VehicleHistoryConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  VehicleHistoryEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },
  JobConnection: {
    edges: (parent) => parent.edges,
    pageInfo: (parent) => parent.pageInfo,
    totalCount: (parent) => parent.totalCount,
  },
  JobEdge: {
    cursor: (parent) => parent.cursor,
    node: (parent) => parent.node,
  },

  # --- Scalar Resolvers (if custom serialization/deserialization is needed) ---
  DateTime: {
    # Example: serialize Date objects to ISO strings
    serialize: (value) => value.toISOString(),
    # Example: parse ISO strings to Date objects
    parseValue: (value) => new Date(value),
    parseLiteral: (ast) => (ast.kind === Kind.STRING ? new Date(ast.value) : null),
  },
  Decimal: {
    # Example: serialize Decimal objects to numbers or strings
    serialize: (value) => parseFloat(value),
    parseValue: (value) => new Decimal(value),
    parseLiteral: (ast) => (ast.kind === Kind.FLOAT || ast.kind === Kind.INT ? new Decimal(ast.value) : null),
  },
  JSON: {
    serialize: (value) => value,
    parseValue: (value) => value,
    parseLiteral: (ast) => (ast.kind === Kind.STRING ? JSON.parse(ast.value) : null),
  },
};

export default resolvers;