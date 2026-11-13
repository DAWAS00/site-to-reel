async page => {
  // Full-page screenshot of out/storyboard-<film>.html, served by the temporary render server.
  // Page URL (open or goto first): http://127.0.0.1:4380/out/storyboard-reel.html?shot=<abs png path>
  const q = new URL(page.url()).searchParams;
  const shot = q.get('shot');
  await page.setViewportSize({ width: 1800, height: 1000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: shot, fullPage: true });
  await page.setViewportSize({ width: 1080, height: 1920 }); // the session is shared with the frame renderer
  return 'ok';
}
