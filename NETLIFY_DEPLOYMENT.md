# Netlify Deployment Guide

## Quick Fix for "Page not found" Error

If you're getting a "Page not found" error on Netlify, follow these steps:

### Step 1: Verify Netlify Configuration

1. Go to your Netlify Dashboard
2. Navigate to **Site settings** → **Build & deploy**
3. Verify these settings:
   - **Base directory**: `frontend` (if your repo root contains both frontend and backend)
   - **Build command**: `npm install && npm run build`
   - **Publish directory**: `dist`

### Step 2: Check Environment Variables

1. Go to **Site settings** → **Environment variables**
2. Add if needed:
   - `VITE_API_BASE_URL` = Your backend API URL (e.g., `https://your-backend.herokuapp.com` or `http://localhost:8000` for local testing)

### Step 3: Verify Files Are Committed

Make sure these files are committed to your repository:

- `netlify.toml` (at root level)
- `frontend/netlify.toml`
- `frontend/public/_redirects`

### Step 4: Trigger a New Deploy

1. Go to **Deploys** tab in Netlify
2. Click **Trigger deploy** → **Clear cache and deploy site**

### Step 5: Verify Build Output

After deployment, check the build logs to ensure:
- The build completed successfully
- The `_redirects` file is in the `dist` folder
- The `index.html` file is in the `dist` folder

## Troubleshooting

### If redirects still don't work:

1. **Check the deploy logs** - Look for any errors during build
2. **Verify the _redirects file** - After build, check if `dist/_redirects` exists
3. **Test the redirect** - Try accessing a route like `/backtest` directly
4. **Check Netlify Functions** - Make sure no functions are interfering

### Alternative: Manual Redirect Configuration

If the `_redirects` file isn't working, you can also set redirects manually in Netlify:

1. Go to **Site settings** → **Redirects and rewrites**
2. Add a new redirect:
   - **From**: `/*`
   - **To**: `/index.html`
   - **Status**: `200`

## File Structure

```
project-root/
├── netlify.toml          # Root level config (if base directory is root)
├── frontend/
│   ├── netlify.toml      # Frontend specific config
│   ├── public/
│   │   └── _redirects    # Redirects file (copied to dist during build)
│   └── dist/             # Build output (after npm run build)
│       ├── index.html
│       └── _redirects    # Should be here after build
```

## Common Issues

1. **Base directory not set**: If your repo has both frontend and backend, set base directory to `frontend`
2. **Build command wrong**: Should be `npm install && npm run build` (not just `npm run build`)
3. **Publish directory wrong**: Should be `dist` (or `frontend/dist` if base is root)
4. **_redirects not copied**: Vite should copy it automatically, but verify it's in `public/` folder

