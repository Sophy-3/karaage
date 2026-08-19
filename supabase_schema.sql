-- Run this once in Supabase SQL Editor before starting the app.
create table if not exists public.users (
  id uuid primary key default gen_random_uuid(), name text not null unique check (char_length(trim(name)) between 1 and 30), created_at timestamptz not null default now()
);
create table if not exists public.categories (
  id uuid primary key default gen_random_uuid(), name text not null unique
);
create table if not exists public.karaage (
  id uuid primary key default gen_random_uuid(), name text not null check (char_length(trim(name)) > 0),
  category_id uuid not null references public.categories(id), recipe_url text not null check (recipe_url ~* '^https?://'),
  created_by uuid not null references public.users(id), created_at timestamptz not null default now()
);
create table if not exists public.user_karaage (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references public.users(id) on delete cascade,
  karaage_id uuid not null references public.karaage(id) on delete cascade, collected_at timestamptz not null default now(), unique (user_id, karaage_id)
);
insert into public.categories (name) values ('肉類'), ('魚介類'), ('野菜類'), ('豆・豆腐類'), ('その他') on conflict (name) do nothing;
alter table public.users enable row level security; alter table public.categories enable row level security; alter table public.karaage enable row level security; alter table public.user_karaage enable row level security;
create policy "phase1 public users" on public.users for all to anon using (true) with check (true);
create policy "phase1 public categories" on public.categories for select to anon using (true);
create policy "phase1 public karaage read" on public.karaage for select to anon using (true);
create policy "phase1 public karaage insert" on public.karaage for insert to anon with check (true);
create policy "phase1 public collections" on public.user_karaage for all to anon using (true) with check (true);
