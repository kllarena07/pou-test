
import React from 'react';
import Head from 'next/head';

class Home extends React.Component {
  // getInitialProps is now outdated, replaced by getServerSideProps/getStaticProps/etc.
  static async getInitialProps(context) {
    // Fetch some data on the server
    const data = await fetch('https://api.example.com/posts').then((res) =>
      res.json()
    );

    return {
      posts: data,
    };
  }

  render() {
    const { posts } = this.props;

    return (
      <div>
        <Head>
          <title>Outdated Next.js Example</title>
        </Head>
        <h1>Outdated Next.js Example</h1>
        <ul>
          {posts.map((post) => (
            <li key={post.id}>{post.title}</li>
          ))}
        </ul>
      </div>
    );
  }
}

export default Home;
