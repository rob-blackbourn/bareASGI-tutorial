import { hot } from 'react-hot-loader'
import React from 'react'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import CssBaseline from '@material-ui/core/CssBaseline'
import Container from '@material-ui/core/Container'
import EditPost from './components/EditPost'
import CreatePost from './components/CreatePost'
import PostViewer from './components/PostViewer'
import Blog from './components/Blog'

const App = () => (
  <Router>
    <CssBaseline />
    <Container maxWidth='sm'>
      <Switch>
        <Route path='/blog/ui/create' component={CreatePost} />
        <Route path='/blog/ui/read/:id' component={PostViewer} />
        <Route path='/blog/ui/update/:id' component={EditPost} />
        <Route path='/blog/ui/index' component={Blog} />
        <Route path='/blog/ui/' component={Blog} />
      </Switch>
    </Container>
  </Router>
)

export default hot(module)(App)
