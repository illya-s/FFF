import React from 'react';
import { renderToString } from 'react-dom/server';
import Legal from './components/pages/support/Legal.jsx';
import axios from 'axios';
import { serverUrl } from './components/Config.jsx';

export async function render() {
    const { data: legal } = await axios.get(`${serverUrl}api/legal/`);
    const appHtml = renderToString(<Legal initialLegal={legal} />);
    return { appHtml, legal };
}