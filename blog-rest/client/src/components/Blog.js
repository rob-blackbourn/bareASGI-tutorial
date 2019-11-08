import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import { Link } from 'react-router-dom'
import Typography from '@material-ui/core/Typography'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction'
import IconButton from '@material-ui/core/IconButton'
import DeleteIcon from '@material-ui/icons/Delete'
import EditIcon from '@material-ui/icons/Edit'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import { API_PATH } from '../config'

const styles = theme => ({
  root: {
  }
})

class Blog extends React.Component {
  state = {
    posts: [],
    error: null
  }

  handleDelete = id => {
    const url = `${API_PATH}/${id}`
    fetch(url, {
      method: 'DELETE'
    })
      .then(request => {
        if (request.ok) {
          this.fetchPosts()
        } else {
          this.setState({ error: 'Delete failed' })
        }
      })
      .catch(error => {
        this.setState({ error: error })
      })
  }

  fetchPosts = () => {
    fetch(API_PATH)
      .then(response => {
        if (response.ok) {
          response.json()
            .then(posts => {
              this.setState({ posts })
            })
            .catch(() => {
              this.setState({ error: 'Failed to fetch posts' })
            })
        }
      })
      .catch(() => {
        this.setState({ error: 'Failed to fetch posts' })
      })
  }

  handleDismissDialog = () => {
    this.setState({ error: null })
  }

  componentDidMount () {
    this.fetchPosts()
  }

  renderDialog = () => {
    return (
      <Dialog onClose={() => this.handleDismissDialog()} open={this.state.error !== null}>
        <DialogTitle>Error</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {this.state.error}
          </DialogContentText>
          <DialogActions>
            <Button onClick={() => this.handleDismissDialog()} color='primary'>
              Dismiss
            </Button>
          </DialogActions>
        </DialogContent>
      </Dialog>
    )
  }

  renderContent = () => {
    const { classes } = this.props
    const { posts } = this.state

    return (
      <div className={classes.root}>
        <Typography variant='h2'>Blog</Typography>

        <List>
          {posts.map(post => (
            <ListItem key={post.id} button component={props => <Link to={`/blog/ui/read/${post.id}`} {...props} />}>
              <ListItemText primary={post.title} secondary={post.description} />
              <ListItemSecondaryAction>
                <IconButton edge='end' aria-label='edit' component={props => <Link to={`/blog/ui/update/${post.id}`} {...props} />}>
                  <EditIcon />
                </IconButton>
                <IconButton edge='end' aria-label='delete' onClick={() => this.handleDelete(post.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        <Link to='/blog/ui/create'>Create a new post</Link>

      </div>
    )
  }

  render () {
    if (this.state.error) {
      return this.renderDialog()
    } else {
      return this.renderContent()
    }
  }
}

Blog.apply.propTypes = {
  classes: PropTypes.object.isRequired
}

export default withStyles(styles)(Blog)
