import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { file } from 'astro/loaders';

const projects = defineCollection({
  loader: file('src/content/projects.json'),
  schema: z.object({
    id: z.string(),
    slug: z.string(),
    title: z.string(),
    category: z.enum(['Products & Client Work', 'Public Repositories']),
    kind: z.string(),
    status: z.string(),
    summary: z.string(),
    overview: z.string(),
    role: z.string().nullable(),
    features: z.array(z.string()),
    challenge: z.string(),
    engineering: z.string(),
    stack: z.array(z.string()),
    validation: z.string(),
    live: z.url().nullable(),
    github: z.url().nullable(),
    capture: z.string(),
    caption: z.string().nullable(),
    gallery: z.array(z.string()),
    order: z.number(),
    demo: z.boolean(),
  }),
});
export const collections = { projects };
