# Configuración de Supabase

## Paso 1: Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta (gratis)
3. Click en **"New Project"**
4. Configura:
   - **Name**: `ai-fitness-agent`
   - **Database Password**: (guarda esta contraseña)
   - **Region**: Selecciona la más cercana
5. Espera ~2 minutos mientras se crea

## Paso 2: Obtener Connection String

1. En tu proyecto de Supabase, ve a **Settings** → **Database**
2. Busca la sección **Connection string**
3. Selecciona **URI** (no Pooler)
4. Copia el string, se verá así:
   ```
   postgresql://postgres:[TU-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
5. Reemplaza `[TU-PASSWORD]` con la contraseña que creaste

## Paso 3: Configurar en Render

1. Ve a tu servicio en [Render Dashboard](https://dashboard.render.com)
2. Click en **"Environment"**
3. Agrega/actualiza la variable:
   - **Key**: `DATABASE_URL`
   - **Value**: (pega tu connection string de Supabase)
4. Click **"Save Changes"**

## Paso 4: Deploy

Render automáticamente redesplegará tu aplicación con la nueva base de datos.

Las migraciones se ejecutarán automáticamente en el primer deploy.

## Verificar Tablas en Supabase

1. Ve a **Table Editor** en Supabase
2. Deberías ver las tablas creadas:
   - `users`
   - `workout_plans`
   - `nutrition_plans`
   - `plan_versions`
   - `plan_comments`
   - `notifications`

## Desarrollo Local con Supabase

Actualiza tu archivo `.env`:

```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
GEMINI_API_KEY=tu_api_key_aquí
```

## Ventajas de Supabase

✅ **Gratis**: 500MB de base de datos, sin límite de tiempo
✅ **Dashboard**: Interfaz visual para ver y editar datos
✅ **Backups**: Automáticos en plan gratuito
✅ **Alta disponibilidad**: Mejor uptime que SQLite
✅ **SQL Editor**: Ejecuta queries directamente en el dashboard

## Troubleshooting

### Error de conexión
- Verifica que el `DATABASE_URL` esté correctamente configurado
- Asegúrate de reemplazar `[TU-PASSWORD]` con tu contraseña real
- Verifica que no haya espacios extras al inicio o final

### Tablas no creadas
- Revisa los logs de build en Render
- Verifica que `build.sh` se ejecutó correctamente
- Ejecuta manualmente: `python -c "from src.infrastructure.database import Base, engine; Base.metadata.create_all(bind=engine)"`
