import { BrowserRouter, Routes, Route } from 'react-router-dom';

import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';

import ThemeWrapper from './context/ThemeWrapper';

import PageNotFound from './templates/shared/components/PageNotFound';
import Chatbot from './templates/shared/components/Chatbot';

function App() {
  return (
    <BrowserRouter>
      <ThemeWrapper>
        <Routes>
          <Route path='/' element={<Chatbot />} />
          <Route path='*' element={<PageNotFound />} />
        </Routes>
      </ThemeWrapper>
    </BrowserRouter>
  );
}

export default App;
