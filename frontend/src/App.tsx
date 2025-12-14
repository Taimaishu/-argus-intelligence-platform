/**
 * Main App component
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { DocumentsPage } from './pages/DocumentsPage';
import { SearchPage } from './pages/SearchPage';
import { ChatPage } from './pages/ChatPage';
import { OSINTPage } from './pages/OSINTPage';
import { CanvasPage } from './pages/CanvasPage';
import { PatternsPage } from './pages/PatternsPage';

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<DocumentsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/osint" element={<OSINTPage />} />
          <Route path="/canvas" element={<CanvasPage />} />
          <Route path="/patterns" element={<PatternsPage />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;
