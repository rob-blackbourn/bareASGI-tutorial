import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import PostEditor from './PostEditor'
import { API_PATH } from '../config'

const styles = theme => ({
  root: {}
})

class CreatePost extends React.Component {
  state = {
    post: {
      title: '',
      description: '',
      content: ''
    },
    isCreated: false,
    error: null
  }

  handleCreate = () => {
    const { post } = this.state

    fetch(API_PATH, {
      method: 'POST',
      body: JSON.stringify({ ...post }),
      headers: new Headers([
        ['content-type', 'application/json']
      ])
    })
      .then(response => {
        if (response.ok) {
          this.setState({ isCreated: true })
        } else {
          this.setState({ error: 'Unable to save post' })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to save post' })
      })
  }

  handleChange = (post, key, value) => {
    this.setState({
      post: {
        ...post,
        [key]: value
      }
    })
  }

  handleDismissDialog = () => {
    this.setState({ error: null })
  }

  renderRedirect = () => {
    return <Redirect to='/blog/ui/index' />
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
    const { post } = this.state

    return (
      <div>
        <Typography variant='h2'>New Post</Typography>

        <PostEditor
          className={classes.root}
          title={post.title}
          onTitleChange={value => this.handleChange(post, 'title', value)}
          description={post.description}
          onDescriptionChange={value => this.handleChange(post, 'description', value)}
          content={post.content}
          onContentChange={value => this.handleChange(post, 'content', value)}
          onSubmit={this.handleCreate}
          submitContent='Create'
        />
      </div>
    )
  }

  render () {
    if (this.state.isCreated === true) {
      return this.renderRedirect()
    } else if (this.state.error) {
      return this.renderDialog()
    } else {
      return this.renderContent()
    }
  }
}

CreatePost.apply.propTypes = {
  classes: PropTypes.object.isRequired
}

export default withStyles(styles)(CreatePost)
