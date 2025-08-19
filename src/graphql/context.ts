import { Request } from 'express';
import { PrismaClient } from '@prisma/client';
import { getUserFromToken } from '../auth';
import { DataLoaders } from './dataloaders';

export interface Context {
  prisma: PrismaClient;
  user?: {
    id: string;
    roles: string[];
  };
  loaders: DataLoaders;
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
    person: new DataLoader(async (ids) => {
      const persons = await prisma.person.findMany({
        where: { person_id: { in: ids } }
      });
      return ids.map(id => persons.find(p => p.person_id === id));
    }),
    // ... other loaders ...
  };
}