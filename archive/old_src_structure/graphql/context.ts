import { Request } from 'express';
import { PrismaClient } from '@prisma/client';
import { getUserFromToken } from '../auth'; // Assuming this function exists
import DataLoader from 'dataloader'; // Import DataLoader

export interface Context {
  prisma: PrismaClient;
  user?: {
    id: string;
    roles: string[];
  };
  loaders: DataLoaders;
}

// Define the interface for all data loaders
export interface DataLoaders {
  person: DataLoader<string, any>;
  company: DataLoader<string, any>;
  vehicle: DataLoader<string, any>;
  personAddress: DataLoader<string, any[]>;
  personContact: DataLoader<string, any[]>;
  companyFinancial: DataLoader<string, any[]>;
  companyRole: DataLoader<string, any[]>;
  vehicleTechnicalSpecs: DataLoader<string, any>;
  vehicleOwnership: DataLoader<string, any[]>;
  vehicleHistory: DataLoader<string, any[]>;
  # Add other loaders as needed
}

export const context = async ({ req }: { req: Request }): Promise<Context> => {
  const prisma = new PrismaClient();
  const token = req.headers.authorization?.split(' ')[1];
  const user = token ? await getUserFromToken(token) : undefined;
  
  return {
    prisma,
    user,
    loaders: createLoaders(prisma),
  };
};

function createLoaders(prisma: PrismaClient): DataLoaders {
  return {
    person: new DataLoader(async (ids: readonly string[]) => {
      const persons = await prisma.person.findMany({
        where: { person_id: { in: ids.map(id => parseInt(id)) } } // Assuming person_id is BigInt
      });
      return ids.map(id => persons.find(p => p.person_id === parseInt(id)));
    }),
    company: new DataLoader(async (ids: readonly string[]) => {
      const companies = await prisma.company.findMany({
        where: { company_id: { in: ids.map(id => parseInt(id)) } }
      });
      return ids.map(id => companies.find(c => c.company_id === parseInt(id)));
    }),
    vehicle: new DataLoader(async (ids: readonly string[]) => {
      const vehicles = await prisma.vehicle.findMany({
        where: { vehicle_id: { in: ids.map(id => parseInt(id)) } }
      });
      return ids.map(id => vehicles.find(v => v.vehicle_id === parseInt(id)));
    }),
    personAddress: new DataLoader(async (personIds: readonly string[]) => {
      const addresses = await prisma.personAddress.findMany({
        where: { person_id: { in: personIds.map(id => parseInt(id)) } }
      });
      // Group addresses by person_id
      const grouped = personIds.map(id => addresses.filter(addr => addr.person_id === parseInt(id)));
      return grouped;
    }),
    personContact: new DataLoader(async (personIds: readonly string[]) => {
      const contacts = await prisma.personContact.findMany({
        where: { person_id: { in: personIds.map(id => parseInt(id)) } }
      });
      const grouped = personIds.map(id => contacts.filter(contact => contact.person_id === parseInt(id)));
      return grouped;
    }),
    companyFinancial: new DataLoader(async (companyIds: readonly string[]) => {
      const financials = await prisma.companyFinancials.findMany({
        where: { company_id: { in: companyIds.map(id => parseInt(id)) } }
      });
      const grouped = companyIds.map(id => financials.filter(fin => fin.company_id === parseInt(id)));
      return grouped;
    }),
    companyRole: new DataLoader(async (companyIds: readonly string[]) => {
      const roles = await prisma.companyRole.findMany({
        where: { company_id: { in: companyIds.map(id => parseInt(id)) } }
      });
      const grouped = companyIds.map(id => roles.filter(role => role.company_id === parseInt(id)));
      return grouped;
    }),
    vehicleTechnicalSpecs: new DataLoader(async (vehicleIds: readonly string[]) => {
      const specs = await prisma.vehicleTechnicalSpecs.findMany({
        where: { vehicle_id: { in: vehicleIds.map(id => parseInt(id)) } }
      });
      return vehicleIds.map(id => specs.find(spec => spec.vehicle_id === parseInt(id)));
    }),
    vehicleOwnership: new DataLoader(async (vehicleIds: readonly string[]) => {
      const ownerships = await prisma.vehicleOwnership.findMany({
        where: { vehicle_id: { in: vehicleIds.map(id => parseInt(id)) } }
      });
      const grouped = vehicleIds.map(id => ownerships.filter(owner => owner.vehicle_id === parseInt(id)));
      return grouped;
    }),
    vehicleHistory: new DataLoader(async (vehicleIds: readonly string[]) => {
      const history = await prisma.vehicleHistory.findMany({
        where: { vehicle_id: { in: vehicleIds.map(id => parseInt(id)) } }
      });
      const grouped = vehicleIds.map(id => history.filter(hist => hist.vehicle_id === parseInt(id)));
      return grouped;
    }),
    # TODO: Add loaders for AnnualReport if it's a separate entity
  };
}