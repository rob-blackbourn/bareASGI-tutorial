import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction'
import IconButton from '@material-ui/core/IconButton'
import DeleteIcon from '@material-ui/icons/Delete'
import EditIcon from '@material-ui/icons/Edit'
import PostIcon from '@material-ui/icons/PostAdd'
import LinkRef from './LinkRef'
import SimpleDialog from './SimpleDialog'
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
          this.setState({ error: 'Unable to delete post' })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to delete post' })
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
      <SimpleDialog
        onClose={() => this.handleDismissDialog()}
        open={this.state.error !== null}
        dialogTitle='Error'
        dialogContent={this.state.error}
      />
    )
  }

  renderContent = () => {
    const { classes } = this.props
    const { posts } = this.state

    return (
      <div className={classes.root}>
        <List>
          {posts.map(post => (
            <ListItem key={post.id} button component={LinkRef} to={`/read/${post.id}`}>
              <ListItemText primary={post.title} secondary={post.description} />
              <ListItemSecondaryAction>
                <IconButton edge='end' aria-label='edit' component={LinkRef} to={`/update/${post.id}`}>
                  <EditIcon />
                </IconButton>
                <IconButton edge='end' aria-label='delete' onClick={() => this.handleDelete(post.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        <IconButton edge='end' aria-label='edit' component={LinkRef} to='/create'>
          <PostIcon />
        </IconButton>

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
