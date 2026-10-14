import { getCollection, type CollectionEntry } from 'astro:content';

export type Project = CollectionEntry<'projects'>['data'];

export async function getProjects(): Promise<Project[]> {
  const entries = await getCollection('projects');
  return entries
    .map((entry) => entry.data)
    .sort((first, second) => first.order - second.order);
}
