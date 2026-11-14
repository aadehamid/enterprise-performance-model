import { MoonIconOutline, SunIconOutline, QuestionMarkCircleIconOutline } from '@neo4j-ndl/react/icons';
import { Typography, CleanIconButton, Logo } from '@neo4j-ndl/react';
import { use } from 'react';
import { ThemeWrapperContext } from '../../../context/ThemeWrapper';

const HELP_URL = import.meta.env.VITE_HELP_URL;

export default function Header({ title }: { title: string }) {
  const { colorMode, toggleColorMode } = use(ThemeWrapperContext);

  return (
    <div className='bg-neutral-bg-weak p-1 border-b-2! border-neutral-border-weak h-16'>
      <nav
        className='flex items-center justify-between'
        role='navigation'
        data-testid='navigation'
        id='navigation'
        aria-label='main navigation'
      >
        <section className='flex md:flex-row flex-col items-center w-0.8 shrink-0 grow-0'>
          <div className='md:inline-block'>
            <Logo className='h-6 min-h-6 min-w-12 md:h-8 md:min-h-12 md:min-w-24 md:mr-2' type='full' />
          </div>
          <div className='flex justify-center md:ml-0 pl-0'>
            <Typography className='md:inline-block hidden' variant='subheading-medium'>
              {title}
            </Typography>
            <Typography className='md:hidden inline-block' variant='subheading-small'>
              {title}
            </Typography>
          </div>
        </section>

        <section className='flex items-center justify-end w-1/6 grow-0'>
          <div className='flex grow-0 gap-x-1 w-max items-center pr-3'>
            <CleanIconButton description='Toggle dark mode' size='large' onClick={toggleColorMode}>
              {colorMode === 'dark' ? (
                <span role='img' aria-label='sun'>
                  <SunIconOutline />
                </span>
              ) : (
                <span role='img' aria-label='moon'>
                  <MoonIconOutline />
                </span>
              )}
            </CleanIconButton>
            {HELP_URL && (
              <CleanIconButton
                onClick={() => window.open(HELP_URL, '_blank', 'noopener,noreferrer')}
                className='hidden md:inline-flex'
                description='Help'
                size='large'
              >
                <QuestionMarkCircleIconOutline aria-hidden='true' />
              </CleanIconButton>
            )}
          </div>
        </section>
      </nav>
    </div>
  );
}
