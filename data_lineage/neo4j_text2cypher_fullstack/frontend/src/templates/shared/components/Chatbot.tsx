import { Suspense, lazy, memo, use, useEffect, useRef, useState } from 'react';
import {
  FilledButton,
  Typography,
  Avatar,
  CleanIconButton,
  LoadingSpinner,
} from '@neo4j-ndl/react';

import { ClipboardDocumentIconOutline } from '@neo4j-ndl/react/icons';

import { PiGraphBold } from "react-icons/pi";

import { HiOutlineThumbDown, HiOutlineThumbUp } from "react-icons/hi";

import { useCopyToClipboard } from '@neo4j-ndl/react';

import './Chatbot.css';
import ReactMarkdown from 'react-markdown';

import remarkGfm from 'remark-gfm';

import Header from './Header';
import { ThemeWrapperContext } from '../../../context/ThemeWrapper';
import { MODEL_LABEL, useAsk } from '../hooks/useAsk';
import type { AskSource, Feedback } from '../api/backend';

const loadRetrievalInformation = () => import('./RetrievalInformation');
const RetrievalInformation = lazy(loadRetrievalInformation);

const REMARK_PLUGINS = [remarkGfm];

const Markdown = memo(function Markdown({ text }: { text: string }) {
  return <ReactMarkdown remarkPlugins={REMARK_PLUGINS}>{text}</ReactMarkdown>;
});

function ChatInput({ isBusy, onAsk, onStop }: { isBusy: boolean; onAsk: (question: string) => void; onStop: () => void }) {
  const [inputMessage, setInputMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustTextareaHeight = () => {
    const tx = textareaRef.current;
    if (tx) {
      tx.style.height = 'auto';
      tx.style.height = `${Math.min(tx.scrollHeight, 120)}px`;
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(e.target.value);
    setTimeout(adjustTextareaHeight, 0);
  };

  const handleSubmit = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    if (!inputMessage.trim()) {
      return;
    }
    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '44px';
    }
    loadRetrievalInformation();
    onAsk(inputMessage);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className='flex gap-2.5 w-full items-end'>
      <textarea
        ref={textareaRef}
        name='question'
        aria-label='Question'
        autoComplete='off'
        style={{
          background: 'var(--theme-color-neutral-bg-weak)',
          border: '1px solid var(--theme-color-neutral-border-strong)',
          borderRadius: '12px',
          color: 'var(--theme-color-neutral-text-default)',
          caretColor: 'var(--theme-color-neutral-text-default)',
          fontFamily: "'Outfit', sans-serif",
          fontSize: '14px',
          padding: '12px',
          minHeight: '44px',
          maxHeight: '120px',
          lineHeight: '1.4',
          outline: 'none',
          resize: 'none',
          transition: 'border-color 0.2s',
        }}
        className='flex-grow w-full focus:border-[#2AADA5] placeholder-opacity-50'
        placeholder='Ask me a question (Press Shift+Enter for new line)...'
        value={inputMessage}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={loadRetrievalInformation}
        rows={1}
      />
      {isBusy ? (
        <FilledButton
          type='button'
          onClick={onStop}
          style={{
            height: '44px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #ef4444, #991b1b)',
            borderColor: '#ef4444',
            boxShadow: '0 4px 14px rgba(239, 68, 68, 0.35)',
            color: '#ffffff',
          }}
        >
          Stop
        </FilledButton>
      ) : (
        <FilledButton type='submit' style={{ height: '44px', borderRadius: '12px' }}>Submit</FilledButton>
      )}
    </form>
  );
}

export default function Chatbot() {
  const isDark = use(ThemeWrapperContext).colorMode === 'dark';
  const { messages: listMessages, result, isAsking: loading, isValidating, isBusy, ask, stop, sendFeedback } = useAsk();
  const [isOpenModal, setIsOpenModal] = useState<boolean>(false);
  const handleCloseModal = () => setIsOpenModal(false);
  const [entitiesModal, setEntitiesModal] = useState<AskSource[]>([]);
  const [modelModal, setModelModal] = useState<string>('');
  const [timeTaken, setTimeTaken] = useState<number>(0);
  const [, copy] = useCopyToClipboard();

  const [feedbackPrompt, setFeedbackPrompt] = useState<{
    msgId: number;
    type: Feedback;
    text: string;
  } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const submitFeedback = async () => {
    if (!feedbackPrompt) return;
    await sendFeedback(feedbackPrompt.type, feedbackPrompt.text);
    setFeedbackPrompt(null);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [listMessages]);

  useEffect(() => {
    if (!isOpenModal) return;
    const closeOnEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpenModal(false);
    };
    document.addEventListener('keydown', closeOnEscape);
    return () => document.removeEventListener('keydown', closeOnEscape);
  }, [isOpenModal]);

  const hasGraph = (result?.graphData?.nodes?.length ?? 0) > 0;
  const hasRows = (result?.rows?.length ?? 0) > 0;

  return (
    <>
      <Header title='Lagos Refining & Supply Company Semantic Portal' />
      <div className='bg-neutral-bg-default flex flex-row min-h-[calc(100vh-64px)] max-h-[calc(100vh-64px)] overflow-hidden'>
        {/* ---- PANE 1: chat (Left 32%) ---- */}
        <div className='flex flex-col justify-between w-[32%] min-w-[320px] max-w-[32%] border-r! border-neutral-border-weak overflow-hidden'>
          <div className='flex-1 overflow-y-auto pb-12 min-w-full'>
            <div className='bg-neutral-bg-default w-full h-full'>
              <div className='flex flex-col gap-3 p-3 pr-6 pl-6'>
                {listMessages.map((chat, index) => {
                  const isPendingReply = loading && index === listMessages.length - 1 && chat.user === 'chatbot';
                  return (
                  <div
                    key={chat.id}
                    className={`flex gap-2.5 items-end ${chat.user === 'chatbot' ? 'flex-row' : 'flex-row-reverse'} `}
                  >
                    <div className='w-8 h-8'>
                      {chat.user === 'chatbot' ? (
                        <Avatar
                          className='-ml-4'
                          hasStatus
                          name='KM'
                          shape='square'
                          size='x-large'
                          status='online'
                          type='image'
                        />
                      ) : (
                        <Avatar
                          className=''
                          hasStatus
                          name='KM'
                          size='x-large'
                          status='online'
                          type='image'
                          shape='square'
                        />
                      )}
                    </div>
                    <div
                      style={{
                        maxWidth: '72%',
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                        borderRadius: '16px',
                        boxShadow: isDark ? '0 4px 20px rgba(0, 0, 0, 0.45)' : '0 4px 16px rgba(0, 0, 0, 0.08)',
                      }}
                      className={`p-4 self-start border! ${
                        chat.user === 'chatbot'
                          ? 'bg-neutral-bg-weak border-neutral-border-strong text-neutral-text-default'
                          : 'bg-primary-bg-weak border-primary-border-weak text-neutral-text-default'
                      }`}
                    >
                      <div
                        style={{
                          wordBreak: 'break-word',
                          overflowWrap: 'break-word',
                        }}
                        className={isPendingReply ? 'loader' : ''}
                      >
                        {isPendingReply ? (
                          <div className='flex flex-col items-center justify-center w-full gap-2'>
                            <LoadingSpinner size='large' className='self-center justify-center align-middle' />
                            {isValidating && (
                              <span style={{ fontSize: '11px', color: isDark ? '#38BDF8' : '#0A6190', fontWeight: 600, marginTop: '8px' }} className='animate-pulse text-center w-full block'>
                                Validating conformed Cypher query path against graph database…
                              </span>
                            )}
                          </div>
                        ) : null}
                        <Markdown text={chat.message} />
                      </div>
                      <div className='text-right align-bottom pt-3'>
                        <Typography variant='body-small'>{chat.datetime}</Typography>
                      </div>
                      <div className='text-right'>
                        {chat.user === 'chatbot' ? (
                          <div className='flex gap-1'>
                            {!chat.isGreeting ? (
                              <>
                                <CleanIconButton
                                  description='Information'
                                  onClick={() => {
                                    setEntitiesModal(chat.entities ?? []);
                                    setModelModal(chat.model ?? '');
                                    setTimeTaken(chat.timeTaken ?? 0);
                                    setIsOpenModal(true);
                                  }}
                                  isDisabled={loading}
                                >
                                  <PiGraphBold style={{ color: isDark ? 'cyan' : '#0097A7' }} className='w-4 h-4 inline-block' aria-hidden='true' />
                                </CleanIconButton>
                                <CleanIconButton isDisabled={loading} description='Copy' onClick={() => copy(chat.message)}>
                                  <ClipboardDocumentIconOutline style={{ color: isDark ? 'white' : 'rgba(0, 0, 0, 0.7)' }} className='w-4 h-4 inline-block' aria-hidden='true' />
                                </CleanIconButton>
                                 <CleanIconButton isDisabled={loading} description='Thumbs up' onClick={() =>  setFeedbackPrompt({ msgId: chat.id, type: 'good', text: '' })}>
                                  <HiOutlineThumbUp style={{ color: isDark ? 'lime' : '#2E7D32' }} className='w-4 h-4 inline-block' aria-hidden='true' />
                                </CleanIconButton>
                                <CleanIconButton isDisabled={loading} description='Thumbs down' onClick={() => setFeedbackPrompt({ msgId: chat.id, type: 'poor', text: '' })}>
                                  <HiOutlineThumbDown style={{ color: isDark ? 'red' : '#C62828' }} className='w-4 h-4 inline-block' aria-hidden='true'/>
                                </CleanIconButton>
                              </>
                            ) : null}
                          </div>
                        ) : (
                          <div className='flex gap-1 justify-end'>
                            <CleanIconButton isDisabled={loading} description='Copy' onClick={() => copy(chat.message)}>
                              <ClipboardDocumentIconOutline style={{ color: isDark ? '#E5E7EB' : 'rgba(0, 0, 0, 0.7)' }} className='w-4 h-4 inline-block' aria-hidden='true' />
                            </CleanIconButton>
                          </div>
                        )}
                        {feedbackPrompt?.msgId === chat.id && (
                          <div style={{
                            marginTop: '12px',
                            padding: '10px',
                            background: 'var(--app-overlay-subtle)',
                            border: '1px solid var(--app-border-subtle)',
                            borderRadius: '10px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '8px',
                          }}>
                            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--app-accent-text)', textAlign: 'left' }}>
                              {feedbackPrompt.type === 'good' ? 'What went well? (Optional)' : 'What could be improved? (Optional)'}
                            </div>
                            <textarea
                              name="feedback"
                              aria-label="Feedback notes"
                              autoComplete="off"
                              placeholder="Type your notes here (Shift+Enter for new line)…"
                              value={feedbackPrompt.text}
                              onChange={(e) => {
                                e.target.style.height = 'auto';
                                e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
                                setFeedbackPrompt({ ...feedbackPrompt, text: e.target.value });
                              }}
                              onKeyDown={async (e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                  e.preventDefault();
                                  await submitFeedback();
                                }
                              }}
                              rows={1}
                              style={{
                                background: 'var(--app-overlay)',
                                border: '1px solid var(--app-border)',
                                borderRadius: '6px',
                                color: 'var(--theme-color-neutral-text-default)',
                                fontSize: '12px',
                                padding: '6px 8px',
                                outline: 'none',
                                fontFamily: "'Outfit', sans-serif",
                                width: '100%',
                                boxSizing: 'border-box',
                                resize: 'none',
                                minHeight: '32px',
                                maxHeight: '100px',
                                lineHeight: '1.4',
                                transition: 'border-color 0.2s',
                              }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                              <button
                                type="button"
                                onClick={() => setFeedbackPrompt(null)}
                                style={{
                                  background: 'transparent',
                                  border: 'none',
                                  color: 'var(--app-text-muted)',
                                  fontSize: '11px',
                                  cursor: 'pointer',
                                }}
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                onClick={submitFeedback}
                                style={{
                                  background: 'linear-gradient(135deg, #2AADA5, #0A6190)',
                                  border: 'none',
                                  borderRadius: '6px',
                                  color: '#FFFFFF',
                                  padding: '4px 10px',
                                  fontSize: '11px',
                                  fontWeight: 600,
                                  cursor: 'pointer',
                                }}
                              >
                                Submit
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>
          <div className='bg-neutral-bg-default flex gap-2.5 bottom-0 p-2.5 w-full border-t! border-neutral-border-weak'>
            <ChatInput isBusy={isBusy} onAsk={ask} onStop={stop} />
          </div>
        </div>

        {/* ---- RIGHT COLUMN: Combined Dashboard Pane & Cypher Query Console (Right 68%) ---- */}
        <div className='flex-1 min-w-[600px] flex flex-col overflow-hidden'>
          {/* Top Section: Lineage Dashboard, Table View & Cypher Tab */}
          <div className='flex-1 min-h-0 overflow-hidden flex flex-col p-4'>
            {result && (hasGraph || hasRows) ? (
              <Suspense
                fallback={
                  <div className='flex items-center justify-center h-full'>
                    <LoadingSpinner size='large' />
                  </div>
                }
              >
                <RetrievalInformation
                  key={result.id}
                  graphData={result.graphData}
                  rows={result.rows}
                  model={result.model}
                  timeTaken={result.timeTaken}
                  cypher={result.cypher}
                  error={result.error}
                  headers={result.headers}
                />
              </Suspense>
            ) : (
              <div className='flex flex-col items-center justify-center h-full p-8 text-center opacity-60'>
                <Typography variant='title-4'>Conversational Search & Semantic Dashboard</Typography>
                <Typography variant='body-medium' className='mt-2'>
                  The interactive lineage graph, tabular view, and Cypher tab render here.
                </Typography>
              </div>
            )}
          </div>
        </div>
      </div>
      {isOpenModal && (
          <div
            role='dialog'
            aria-modal='true'
            aria-labelledby='query-metadata-title'
            style={{
            overscrollBehavior: 'contain',
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0, 0, 0, 0.65)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 9999,
          }}>
            <div style={{
              background: '#070A13',
              border: '2px solid #2AADA5',
              borderRadius: '20px',
              width: '90%',
              maxWidth: '500px',
              padding: '24px',
              boxShadow: '0 12px 48px 0 rgba(0, 0, 0, 0.6)',
              position: 'relative',
              fontFamily: "'Outfit', sans-serif",
              color: '#FFFFFF',
            }}>
              <button
                type="button"
                aria-label="Close"
                onClick={handleCloseModal}
                style={{
                  position: 'absolute',
                  top: '16px',
                  right: '20px',
                  background: 'transparent',
                  border: 'none',
                  color: '#ffffff',
                  fontSize: '22px',
                  cursor: 'pointer',
                  opacity: 0.6,
                  transition: 'opacity 0.2s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.opacity = '1'; }}
                onMouseLeave={(e) => { e.currentTarget.style.opacity = '0.6'; }}
              >
                ✕
              </button>
              <h3 id='query-metadata-title' style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#38BDF8', fontWeight: 700 }}>
                Lineage Query Metadata
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px' }}>
                <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '8px' }}>
                  <span style={{ fontWeight: 600, color: 'rgba(255,255,255,0.6)' }}>Parser Model:</span>
                  <div style={{ marginTop: '4px', fontWeight: 500 }}>{modelModal || MODEL_LABEL}</div>
                </div>
                
                <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '8px' }}>
                  <span style={{ fontWeight: 600, color: 'rgba(255,255,255,0.6)' }}>Execution Speed:</span>
                  <div style={{ marginTop: '4px', fontWeight: 500 }}>
                    {(timeTaken / 1000).toFixed(3)} seconds ({timeTaken} ms)
                  </div>
                </div>

                <div>
                  <span style={{ fontWeight: 600, color: 'rgba(255,255,255,0.6)' }}>Graph Lineage Sources:</span>
                  <div style={{ 
                    marginTop: '8px', 
                    maxHeight: '200px',
                    overscrollBehavior: 'contain',
                    overflowY: 'auto', 
                    background: 'rgba(255,255,255,0.02)', 
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '10px',
                    padding: '10px'
                  }}>
                    {entitiesModal && entitiesModal.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {entitiesModal.map((entity, idx) => {
                          const val = entity?.graph_data?.nodes?.[0]?.properties?.qualifiedName || 
                                      entity?.graph_data?.nodes?.[0]?.properties?.name || 
                                      entity?.graph_data?.nodes?.[0]?.properties?.serverName ||
                                      'Conformed lineage elements';
                          return (
                            <div key={idx} style={{ 
                              fontSize: '12px', 
                              padding: '6px 8px',
                              background: 'rgba(255,255,255,0.04)',
                              borderRadius: '6px',
                              overflowWrap: 'anywhere',
                              fontFamily: 'monospace'
                            }}>
                              {val}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div style={{ fontSize: '12px', opacity: 0.5 }}>No entities recorded for this lineage hop.</div>
                    )}
                  </div>
                </div>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button 
                  type="button"
                  onClick={handleCloseModal}
                  style={{
                    background: 'linear-gradient(135deg, #2AADA5, #0A6190)',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#FFFFFF',
                    padding: '8px 16px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    boxShadow: '0 4px 15px rgba(42, 173, 165, 0.35)',
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }
