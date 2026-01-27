# 🚀 Deployment Guide - Render

## Files Added/Modified

The following files were created for API integration:

### Documentation Files (No deployment needed - for reference only)
- ✅ `API_DOCUMENTATION.md`
- ✅ `INTEGRATION_GUIDE.md`
- ✅ `README_API.md`
- ✅ `GETTING_STARTED.md`
- ✅ `FILE_OVERVIEW.md`
- ✅ `QUICK_REFERENCE.txt`

### Code Files (Need to be deployed)
- ⚠️ `static/chatbot-widget.js` - **IMPORTANT: This needs to be deployed!**
- ✅ `examples/chatbot-widget.js` - (Reference copy, not served)
- ✅ `examples/simple-integration.html` - (Example, not served)
- ✅ `examples/custom-ui.html` - (Example, not served)
- ✅ `examples/react-chatbot/Chatbot.jsx` - (Example, not served)
- ✅ `examples/test_api.py` - (Test script, not served)

---

## ⚠️ DO YOU NEED TO DEPLOY?

**YES**, you need to deploy because:

1. **New file added**: `static/chatbot-widget.js` - This is the embeddable widget that will be served from your API
2. This file needs to be publicly accessible at: `https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js`

**Documentation files** (`.md` files) don't need deployment - they're just for reference.

---

## 📋 Complete Deployment Steps

### Step 1: Check Current Status
```bash
# See what files are new/modified
git status
```

**Expected output**: You should see untracked files including `static/chatbot-widget.js`

---

### Step 2: Add Files to Git

```bash
# Add the important widget file
git add static/chatbot-widget.js

# Optionally add documentation files (good for version control)
git add API_DOCUMENTATION.md
git add INTEGRATION_GUIDE.md
git add README_API.md
git add GETTING_STARTED.md
git add FILE_OVERVIEW.md
git add QUICK_REFERENCE.txt

# Add all example files
git add examples/
```

**Or add everything at once:**
```bash
git add .
```

---

### Step 3: Commit Changes

```bash
git commit -m "Add chatbot widget and API integration documentation"
```

---

### Step 4: Push to GitHub/Repository

```bash
git push origin main
```

**Note**: Replace `main` with your branch name if different (could be `master`)

---

### Step 5: Render Auto-Deploy

If you have **auto-deploy enabled** on Render (which is common):
- ✅ Render will automatically detect the push
- ✅ It will start building and deploying
- ✅ Wait 2-5 minutes for deployment to complete

**Check deployment status:**
1. Go to https://dashboard.render.com
2. Click on your service (`chat-agent-9wt6`)
3. Check the "Events" tab to see deployment progress

---

### Step 6: Verify Deployment

After deployment completes, test if the widget is accessible:

**Method 1: Browser**
Open this URL in your browser:
```
https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js
```

You should see the JavaScript code for the widget.

**Method 2: cURL**
```bash
curl https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js
```

**Method 3: Test the widget**
Create a simple HTML file and test:
```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <h1>Testing Widget</h1>
  <script src="https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js"></script>
  <script>
    ChatbotWidget.init({
      apiUrl: 'https://chat-agent-9wt6.onrender.com'
    });
  </script>
</body>
</html>
```

---

## 🔄 If Auto-Deploy is NOT Enabled

If Render doesn't auto-deploy:

1. Go to https://dashboard.render.com
2. Click on your service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Widget file is accessible: `https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js`
- [ ] API endpoints still work: `https://chat-agent-9wt6.onrender.com/api/chat`
- [ ] Test the widget on a sample HTML page
- [ ] Check Render logs for any errors

---

## 🧪 Quick Test After Deployment

Run the Python test script:
```bash
cd examples
python test_api.py
```

Or test in browser console:
```javascript
fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello!' })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 📊 Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Git add & commit | 1 min | Local |
| Git push | 1 min | Upload |
| Render build | 2-3 min | Building |
| Render deploy | 1-2 min | Deploying |
| **Total** | **5-7 min** | ✅ Live |

---

## 🚨 Troubleshooting

### Widget file not found (404)
**Solution**: 
- Check if file exists in `static/` folder
- Verify it was committed and pushed
- Check Render logs for deployment errors

### Deployment failed
**Solution**:
- Check Render logs for error messages
- Verify `requirements.txt` is up to date
- Check if there are any syntax errors

### Old version still showing
**Solution**:
- Clear browser cache (Ctrl+Shift+R)
- Wait a few more minutes for CDN to update
- Check Render dashboard to confirm deployment completed

---

## 📝 Summary

**What you need to do:**

1. ✅ Add files: `git add .`
2. ✅ Commit: `git commit -m "Add chatbot widget and API docs"`
3. ✅ Push: `git push origin main`
4. ✅ Wait 5-7 minutes for Render to deploy
5. ✅ Verify: Open `https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js`

**That's it!** Your widget will be live and ready to use on any website.

---

## 🎯 Next Steps After Deployment

1. Test the widget on a sample HTML page
2. Share the integration code with your team
3. Update your website with the widget
4. Monitor usage via `/api/analytics`

---

## 💡 Pro Tips

- **Always test locally first** before deploying
- **Check Render logs** if something goes wrong
- **Keep documentation updated** when you make changes
- **Use git tags** for important releases: `git tag v1.0.0`
- **Monitor your app** on Render dashboard

---

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- Your API: https://chat-agent-9wt6.onrender.com
- Widget URL: https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js

---

**Ready to deploy? Follow the steps above!** 🚀
