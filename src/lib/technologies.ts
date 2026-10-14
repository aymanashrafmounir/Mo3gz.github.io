export const technologyIcons: Record<string, string> = {
  Java: 'java',
  'Spring Boot': 'spring',
  TypeScript: 'typescript',
  React: 'react',
  Python: 'python',
  'C++': 'cplusplus',
  'Qt 6': 'qt',
  Qt: 'qt',
  PostgreSQL: 'postgresql',
  MySQL: 'mysql',
  SQLite: 'sqlite',
  Docker: 'docker',
  Git: 'git',
  Vitest: 'vitest',
  Playwright: 'playwright',
  JavaScript: 'javascript',
  Cloudflare: 'cloudflare',
  'Cloudflare Workers': 'cloudflare',
  Workers: 'cloudflare',
};

export function displayStack(technologies: string[]) {
  return technologies
    .filter((technology) => technologyIcons[technology])
    .slice(0, 3);
}
