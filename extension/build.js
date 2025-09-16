const fs = require('fs-extra');
const { execSync } = require('child_process');
const archiver = require('archiver');
const extract = require('extract-zip');
const path = require('path');

const config = {
    packageName: 'homepage-extension',
    distDir: 'dist',
    releasesDir: 'releases',
    unpackedDir: 'unpacked',
    staticRootFiles: ['manifest.json']
};

async function main() {
    try {
        // 1. Clean up old build directories
        console.log('[-] Cleaning up old build directories...');
        fs.emptyDirSync(config.distDir);
        fs.emptyDirSync(config.unpackedDir);

        // 2. Compile TypeScript
        console.log('[+] Compiling TypeScript...');
        execSync('npm run compile --silent', { stdio: 'inherit' });

        // 3. Build React popup
        console.log('[+] Building React popup...');
        execSync('cd popup && npm run build --silent', { stdio: 'inherit' });

        // 4. Copy static assets
        console.log(`[+] Copying static assets to ${config.distDir}...`);
        for (const file of config.staticRootFiles) {
            if (fs.existsSync(file)) {
                fs.copySync(file, path.join(config.distDir, file));
            }
        }

        // Copy built popup from popup/dist to dist/popup
        if (fs.existsSync('popup/dist')) {
            fs.copySync('popup/dist', path.join(config.distDir, 'popup'));
        }

        // Copy icons
        if (fs.existsSync('icons')) {
            fs.copySync('icons', path.join(config.distDir, 'icons'), {
                filter: (src) => !src.endsWith('.ts')
            });
        }

        // 4. Create release package
        console.log('[*] Creating release package...');
        const { zipPath } = await createReleasePackage();
        console.log(`[SUCCESS] Created new release: ${zipPath}`);

        // 5. Create unpacked version
        await createUnpackedVersion(zipPath);
        console.log(`[SUCCESS] Created unpacked version for testing at: ${path.resolve(config.unpackedDir)}`);

    } catch (error) {
        console.error('[ERROR] Build process failed:', error);
        process.exit(1);
    }
}

function createReleasePackage() {
    return new Promise((resolve, reject) => {
        fs.ensureDirSync(config.releasesDir);

        const manifest = JSON.parse(fs.readFileSync('manifest.json', 'utf-8'));
        const version = manifest.version;

        const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const existingBuilds = fs.readdirSync(config.releasesDir).filter(f => f.startsWith(`${config.packageName}-v${version}-${date}`)).length;
        const buildNum = existingBuilds + 1;
        const fileName = `${config.packageName}-v${version}-${date}-${buildNum}.zip`;
        const zipPath = path.join(config.releasesDir, fileName);

        const output = fs.createWriteStream(zipPath);
        const archive = archiver('zip', { zlib: { level: 9 } });

        output.on('close', () => resolve({ zipPath }));
        archive.on('error', (err) => reject(err));

        archive.pipe(output);
        archive.directory(config.distDir, false);
        archive.finalize();
    });
}

async function createUnpackedVersion(zipPath) {
    fs.ensureDirSync(config.unpackedDir);
    await extract(zipPath, { dir: path.resolve(config.unpackedDir) });
}

main(); 