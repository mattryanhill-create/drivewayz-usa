export async function POST(request) {
  try {
    const body = await request.json();
    const urls = body?.urls;

    if (!Array.isArray(urls)) {
      return Response.json(
        { error: 'Request body must include a "urls" array' },
        { status: 400 }
      );
    }

    const indexNowBody = {
      host: 'drivewayzusa.co',
      key: 'd6a18339e6cf4dc6b9f826a6ceac70d9',
      keyLocation: 'https://drivewayzusa.co/d6a18339e6cf4dc6b9f826a6ceac70d9.txt',
      urlList: urls,
    };

    const response = await fetch('https://api.indexnow.org/IndexNow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify(indexNowBody),
    });

    const text = await response.text();
    let data = {};
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }
    }

    return Response.json(
      { success: response.ok, status: response.status, ...data },
      { status: response.ok ? 200 : response.status }
    );
  } catch (error) {
    return Response.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}
