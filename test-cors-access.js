#!/usr/bin/env node
/**
 * Test CORS proxy access to GitLab repository
 * Tests authentication and branch listing via cors.isomorphic-git.org
 */

const token = process.env.GITLAB_TOKEN || 'glpat-XXXXXXXXXXXXXXXXXXXX'; // Set via env var or edit here
const user = 'alvarogarcia8110';
const repo = 'https://gitlab.crypto.tii.ae/agb-project-incubator/training-parser-data.git';
const corsProxy = 'https://cors.isomorphic-git.org';

console.log('🔍 Testing GitLab Repository Access via CORS Proxy\n');
console.log('Configuration:');
console.log(`  Repository: ${repo}`);
console.log(`  User: ${user}`);
console.log(`  CORS Proxy: ${corsProxy}\n`);

async function testDirectAccess() {
  console.log('1️⃣ Testing direct access (no auth)...');
  try {
    const url = `${repo}/info/refs?service=git-upload-pack`;
    console.log(`   URL: ${url}`);
    const resp = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': '*/*' },
    });
    console.log(`   Status: ${resp.status} ${resp.statusText}`);
    const text = await resp.text();
    console.log(`   Response length: ${text.length} bytes`);
    if (resp.status === 401 || resp.status === 403) {
      console.log(`   ✅ Rejected (expected - needs auth)\n`);
      return false;
    } else if (resp.ok) {
      console.log(`   ✅ Accessible without auth\n`);
      return true;
    } else {
      console.log(`   ❌ Unexpected status\n`);
      return false;
    }
  } catch (e) {
    console.log(`   ❌ Failed: ${e.message}\n`);
    return false;
  }
}

async function testWithBasicAuth() {
  console.log('2️⃣ Testing with basic auth (no proxy)...');
  try {
    const auth = Buffer.from(`${user}:${token}`).toString('base64');
    const url = `${repo}/info/refs?service=git-upload-pack`;
    console.log(`   URL: ${url}`);
    console.log(`   Auth: Basic ${auth.substring(0, 20)}...`);

    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
        'Authorization': `Basic ${auth}`,
      },
    });
    console.log(`   Status: ${resp.status} ${resp.statusText}`);
    const text = await resp.text();
    console.log(`   Response length: ${text.length} bytes`);

    if (resp.ok) {
      console.log(`   ✅ Auth works! GitLab is accessible\n`);
      return true;
    } else if (resp.status === 401 || resp.status === 403) {
      console.log(`   ❌ Auth failed (invalid credentials?)\n`);
      return false;
    } else {
      console.log(`   ❌ Unexpected status\n`);
      return false;
    }
  } catch (e) {
    console.log(`   ❌ Failed: ${e.message}\n`);
    return false;
  }
}

async function testViaCorProxy() {
  console.log('3️⃣ Testing via CORS proxy with auth...');
  try {
    const auth = Buffer.from(`${user}:${token}`).toString('base64');
    // Correct format: https://cors.isomorphic-git.org/https://example.com/path
    const targetUrl = `${repo}/info/refs?service=git-upload-pack`;
    const url = `${corsProxy}/${targetUrl}`;
    console.log(`   Proxied URL: ${corsProxy}/...`);
    console.log(`   Target: ${targetUrl}`);
    console.log(`   Auth header: Basic ${auth.substring(0, 20)}...`);

    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
        'Authorization': `Basic ${auth}`,
      },
    });
    console.log(`   Status: ${resp.status} ${resp.statusText}`);
    const text = await resp.text();
    console.log(`   Response length: ${text.length} bytes`);

    if (text.length < 500) {
      console.log(`   Response: ${text.substring(0, 200)}`);
    } else {
      console.log(`   Response preview: ${text.substring(0, 100)}`);
      if (text.includes('403') || text.includes('Forbidden')) {
        console.log(`   Response contains: 403 Forbidden error`);
      }
    }

    if (resp.ok) {
      console.log(`   ✅ CORS proxy works! Can access GitLab through proxy\n`);
      return true;
    } else if (resp.status === 401 || resp.status === 403) {
      console.log(`   ⚠️  Auth may not be passing through proxy (403/401 from GitLab)`);
      console.log(`   Note: CORS proxy might not forward Authorization headers\n`);
      return false;
    } else {
      console.log(`   ❌ Unexpected status via proxy\n`);
      return false;
    }
  } catch (e) {
    console.log(`   ❌ Failed: ${e.message}\n`);
    return false;
  }
}

async function testViaCorProxyWithEmbeddedAuth() {
  console.log('3b️⃣ Testing via CORS proxy with embedded auth in URL...');
  try {
    // Try embedding auth in URL: https://user:token@host/path
    const repoWithAuth = repo.replace('https://', `https://${user}:${token}@`);
    const targetUrl = `${repoWithAuth}/info/refs?service=git-upload-pack`;
    const url = `${corsProxy}/${targetUrl}`;
    console.log(`   Target with embedded auth: https://${user}:***@gitlab.crypto.tii.ae/...`);

    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
      },
    });
    console.log(`   Status: ${resp.status} ${resp.statusText}`);
    const text = await resp.text();
    console.log(`   Response length: ${text.length} bytes`);

    if (resp.ok) {
      console.log(`   ✅ CORS proxy with embedded auth works!\n`);
      return true;
    } else if (resp.status === 401 || resp.status === 403) {
      console.log(`   ❌ Auth still failed even with embedded credentials\n`);
      return false;
    } else {
      console.log(`   ⚠️  Status: ${resp.status}\n`);
      return false;
    }
  } catch (e) {
    console.log(`   ❌ Failed: ${e.message}\n`);
    return false;
  }
}

async function testListRefs() {
  console.log('4️⃣ Testing ref listing (simulate isomorphic-git)...');
  try {
    const auth = Buffer.from(`${user}:${token}`).toString('base64');
    // isomorphic-git format: query refs from advertised-refs
    const targetUrl = `${repo}/info/refs?service=git-upload-pack`;
    const url = `${corsProxy}/${targetUrl}`;

    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
        'Authorization': `Basic ${auth}`,
        'User-Agent': 'isomorphic-git/test',
      },
    });

    if (!resp.ok) {
      console.log(`   ❌ Failed to fetch refs: ${resp.status}\n`);
      return false;
    }

    const text = await resp.text();
    const lines = text.split('\n').filter(l => l.trim());
    console.log(`   Found ${lines.length} ref lines`);

    const branchLines = lines.filter(l => l.includes('refs/heads/'));
    console.log(`   Branches found: ${branchLines.length}`);

    branchLines.forEach(line => {
      const match = line.match(/refs\/heads\/([^\s]+)/);
      if (match) console.log(`     - ${match[1]}`);
    });

    if (branchLines.length > 0) {
      console.log(`   ✅ Successfully listed branches\n`);
      return true;
    } else {
      console.log(`   ⚠️  No branches found (repo might be empty)\n`);
      return true; // Still a successful connection
    }
  } catch (e) {
    console.log(`   ❌ Failed: ${e.message}\n`);
    return false;
  }
}

async function runTests() {
  console.log('═'.repeat(60) + '\n');

  const direct = await testDirectAccess();
  const auth = await testWithBasicAuth();
  const cors = await testViaCorProxy();
  const corsEmbedded = await testViaCorProxyWithEmbeddedAuth();
  const refs = await testListRefs();

  console.log('═'.repeat(60));
  console.log('\n📊 Test Summary:\n');
  console.log(`  Direct access (no auth):         ${direct ? '✅' : '❌'}`);
  console.log(`  Direct access (with auth):       ${auth ? '✅' : '❌'}`);
  console.log(`  CORS proxy (auth header):        ${cors ? '✅' : '❌'}`);
  console.log(`  CORS proxy (embedded auth):      ${corsEmbedded ? '✅' : '❌'}`);
  console.log(`  Ref listing:                     ${refs ? '✅' : '❌'}`);

  console.log('\n🔍 Diagnosis:');
  if (auth) {
    console.log(`  ✅ GitLab credentials are valid`);
    console.log(`  ✅ Direct connection works`);
  }
  if (!cors && corsEmbedded) {
    console.log(`  ⚠️  CORS proxy doesn't forward Authorization headers`);
    console.log(`  ✅ But works with embedded auth in URL`);
  } else if (cors) {
    console.log(`  ✅ CORS proxy forwards Authorization headers`);
  }

  if (auth && (cors || corsEmbedded)) {
    console.log('\n✅ Access works! PWA should be able to sync via CORS proxy.\n');
    process.exit(0);
  } else {
    console.log('\n⚠️  Access issues detected. See diagnosis above.\n');
    process.exit(1);
  }
}

runTests().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});
