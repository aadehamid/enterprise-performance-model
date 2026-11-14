import { FilledButton, Flex, Typography } from '@neo4j-ndl/react';
import { useNavigate } from 'react-router-dom';

export default function PageNotFound() {
  const navigate = useNavigate();

  return (
    <div className='bg-neutral-bg-default flex items-center justify-center min-h-screen p-12'>
      <Flex gap='8'>
        <Typography variant='title-1'>404 - Page Not Found</Typography>
        <Typography variant='body-medium'>
          <p>It looks like the page you are trying to access either does not exists or is currently unavailable</p>
          <p>Please try again later and if the problem persists contact us</p>
        </Typography>
        <FilledButton onClick={() => navigate(-1)}>Go back</FilledButton>
      </Flex>
    </div>
  );
}
